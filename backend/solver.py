import random
import re
import time
from copy import deepcopy


NO_SOLUTION_MESSAGE = "No valid seating arrangement found for current constraints and hall capacities."


class SeatingSolver:
    """CSP-style examination seating engine.

    CSP model:
    - Variables: each student.
    - Domains: every usable seat across all configured halls.
    - Constraints: blocked seats, one student per seat, and same-subject
      adjacency rules. Branch is used as the subject grouping until the CSV
      includes a dedicated subject/course column.
    """

    def generate(self, students, halls, constraints=None, shuffle=False):
        constraints = constraints or {}
        normalized_halls = self._normalize_halls(halls)
        seats = self._build_domains(normalized_halls)

        if len(students) > len(seats):
            return self._failure(
                normalized_halls,
                students,
                seats,
                "Insufficient seating capacity",
                f"{len(students)} students require seats, but only {len(seats)} usable seats are available.",
            )

        arrangements = []
        signatures = set()
        attempts = 5 if shuffle else 4
        for attempt_index in range(attempts):
            arrangement = self._solve_once(
                students,
                normalized_halls,
                seats,
                constraints,
                randomize=shuffle or attempt_index > 0,
                attempt_index=attempt_index,
            )
            if arrangement is None:
                continue
            signature = self._arrangement_signature(arrangement["halls"])
            if signature in signatures:
                continue
            signatures.add(signature)
            arrangement["id"] = f"arrangement-{len(arrangements) + 1}"
            arrangement["label"] = f"Arrangement {chr(65 + len(arrangements))}"
            arrangements.append(arrangement)
            if len(arrangements) == 3:
                break

        if not arrangements:
            return self._failure(
                normalized_halls,
                students,
                seats,
                "Same-subject separation constraints are too strict for available hall capacity",
                "Seats are available, but no assignment satisfies the selected separation policy. Relax the policy or increase hall capacity.",
            )

        while len(arrangements) < 3:
            duplicate = deepcopy(arrangements[-1])
            duplicate["id"] = f"arrangement-{len(arrangements) + 1}"
            duplicate["label"] = f"Arrangement {chr(65 + len(arrangements))}"
            duplicate["warnings"] = ["The search space produced fewer than three unique valid layouts."]
            arrangements.append(duplicate)

        primary = deepcopy(arrangements[0])
        primary["arrangements"] = arrangements
        primary["selectedArrangementId"] = primary["id"]
        return primary

    def _solve_once(self, students, halls, seats, constraints, randomize, attempt_index):
        same_subject_mode = constraints.get("sameSubjectHandling", "prevent-adjacent")
        include_diagonal = bool(constraints.get("includeDiagonalAdjacency", False))
        variables = self._build_variables(students, randomize)
        domains = {variable["id"]: list(seats) for variable in variables}
        if randomize:
            for domain in domains.values():
                random.shuffle(domain)

        self._metrics = {
            "assignments": 0,
            "backtracks": 0,
            "pruned": 0,
            "recursiveCalls": 0,
            "mrvSelections": 0,
        }
        blocked_count = sum(len(hall["blockedSeats"]) for hall in halls)
        self._trace = [
            f"Loaded {len(students)} students as CSP variables.",
            f"Loaded {len(halls)} halls with {len(seats)} usable seat-domain values.",
            f"Preprocessed {blocked_count} blocked seats and removed them from domains.",
            f"Applied same-subject policy: {same_subject_mode.replace('-', ' ')}.",
        ]
        started_at = time.perf_counter()
        assignment = self._backtrack(
            variables=variables,
            domains=domains,
            assignment={},
            same_subject_mode=same_subject_mode,
            include_diagonal=include_diagonal,
        )
        self._metrics["solveTime"] = round(time.perf_counter() - started_at, 4)
        if assignment is None:
            return None

        self._trace.extend([
            f"MRV heuristic selected the next variable {self._metrics['mrvSelections']} times.",
            f"Forward checking pruned {self._metrics['pruned']} invalid seat options.",
            f"Backtracking recovered from {self._metrics['backtracks']} dead ends.",
            f"Solution found after {self._metrics['recursiveCalls']} recursive calls.",
        ])
        output = self._build_output(halls, variables, assignment)
        output.update(self._evaluate(output["halls"], halls, same_subject_mode, include_diagonal))
        output["trace"] = list(self._trace)
        output["metrics"] = dict(self._metrics)
        output["searchAttempt"] = attempt_index + 1
        return output

    def _backtrack(self, variables, domains, assignment, same_subject_mode, include_diagonal):
        """Recursive backtracking search over student-seat assignments."""
        self._metrics["recursiveCalls"] += 1
        if len(assignment) == len(variables):
            return assignment

        variable = self._select_unassigned_variable_mrv(variables, domains, assignment)
        if variable is None:
            return None

        for seat in list(domains[variable["id"]]):
            self._metrics["assignments"] += 1
            if not self.is_valid_assignment(variable, seat, assignment, same_subject_mode, include_diagonal):
                continue

            next_assignment = {**assignment, variable["id"]: seat}
            next_domains = self._forward_check(
                variables=variables,
                domains=deepcopy(domains),
                assignment=next_assignment,
                assigned_variable=variable,
                assigned_seat=seat,
                same_subject_mode=same_subject_mode,
                include_diagonal=include_diagonal,
            )

            if next_domains is None:
                continue

            result = self._backtrack(
                variables=variables,
                domains=next_domains,
                assignment=next_assignment,
                same_subject_mode=same_subject_mode,
                include_diagonal=include_diagonal,
            )
            if result is not None:
                return result

        self._metrics["backtracks"] += 1
        return None

    def _forward_check(
        self,
        variables,
        domains,
        assignment,
        assigned_variable,
        assigned_seat,
        same_subject_mode,
        include_diagonal,
    ):
        """Prune domains after assigning a seat.

        Forward checking removes the occupied seat from all remaining domains.
        For same-subject constraints, it also removes neighboring seats from
        unassigned students in the same Branch group.
        """
        for variable in variables:
            variable_id = variable["id"]
            if variable_id in assignment:
                continue

            previous_size = len(domains[variable_id])
            domains[variable_id] = [seat for seat in domains[variable_id] if seat != assigned_seat]

            if self.check_subject_conflict(assigned_variable, variable, same_subject_mode):
                blocked_neighbors = set(self.get_neighboring_seats(
                    assigned_seat,
                    mode=same_subject_mode,
                    include_diagonal=include_diagonal,
                ))
                domains[variable_id] = [seat for seat in domains[variable_id] if seat not in blocked_neighbors]

            self._metrics["pruned"] += previous_size - len(domains[variable_id])

            if not domains[variable_id]:
                return None

        return domains

    def _select_unassigned_variable_mrv(self, variables, domains, assignment):
        """MRV heuristic: pick the unassigned student with the smallest domain."""
        unassigned = [variable for variable in variables if variable["id"] not in assignment]
        if not unassigned:
            return None
        self._metrics["mrvSelections"] += 1
        return min(unassigned, key=lambda variable: len(domains[variable["id"]]))

    def is_valid_assignment(self, variable, seat, assignment, same_subject_mode, include_diagonal=False):
        """Validate one candidate student-seat assignment against current state."""
        if seat in assignment.values():
            return False

        for assigned_student_id, assigned_seat in assignment.items():
            assigned_variable = self._student_by_id(variable["all_variables"], assigned_student_id)
            if not self.check_subject_conflict(variable, assigned_variable, same_subject_mode):
                continue

            neighbors = self.get_neighboring_seats(
                assigned_seat,
                mode=same_subject_mode,
                include_diagonal=include_diagonal,
            )
            if seat in neighbors:
                return False

        return True

    def get_neighboring_seats(self, seat, mode="prevent-adjacent", include_diagonal=False):
        """Return seats that conflict with a seat under the selected mode.

        Horizontal and vertical adjacency are always included. Diagonal
        adjacency is optional. Leave-one-seat-gap expands the radius to two
        seats, creating a simple gap around same-subject students.
        """
        hall_index, row_index, col_index = seat
        radius = 2 if mode == "leave-one-seat-gap" else 1
        neighbors = set()

        for row_delta in range(-radius, radius + 1):
            for col_delta in range(-radius, radius + 1):
                if row_delta == 0 and col_delta == 0:
                    continue

                is_horizontal = row_delta == 0 and col_delta != 0
                is_vertical = col_delta == 0 and row_delta != 0
                is_diagonal = abs(row_delta) == abs(col_delta)

                if not (is_horizontal or is_vertical or (include_diagonal and is_diagonal)):
                    continue

                neighbors.add((hall_index, row_index + row_delta, col_index + col_delta))

        return neighbors

    def check_subject_conflict(self, student_a, student_b, same_subject_mode):
        """Return True when two students should not be close to each other."""
        if same_subject_mode == "allow-adjacent":
            return False
        return student_a.get("Branch") == student_b.get("Branch")

    def _build_variables(self, students, shuffle):
        variables = []
        for index, student in enumerate(students):
            variables.append({
                "id": str(student.get("RollNo") or index),
                "RollNo": str(student.get("RollNo", "")),
                "Name": str(student.get("Name", "")),
                "Branch": str(student.get("Branch", "")),
            })

        if shuffle:
            random.shuffle(variables)

        for variable in variables:
            variable["all_variables"] = variables

        return variables

    def _build_domains(self, halls):
        domains = []
        for hall_index, hall in enumerate(halls):
            for row_index in range(hall["rows"]):
                for col_index in range(hall["cols"]):
                    seat = (hall_index, row_index, col_index)
                    if seat not in hall["blockedSeats"]:
                        domains.append(seat)
        return domains

    def _normalize_halls(self, halls):
        normalized = []
        for hall_index, hall in enumerate(halls):
            rows = int(hall.get("rows") or 0)
            cols = int(hall.get("cols") or hall.get("columns") or 0)
            blocked = self._parse_blocked_seats(hall.get("blockedSeats"), hall_index, rows, cols)
            normalized.append({
                "hallName": hall.get("hallName") or "Unnamed Hall",
                "rows": rows,
                "cols": cols,
                "blockedSeats": blocked,
            })
        return normalized

    def _build_output(self, halls, variables, assignment):
        student_lookup = {variable["id"]: self._public_student(variable) for variable in variables}
        assigned_by_seat = {seat: student_lookup[student_id] for student_id, seat in assignment.items()}
        output_halls = []

        for hall_index, hall in enumerate(halls):
            seating = []
            for row_index in range(hall["rows"]):
                row = []
                for col_index in range(hall["cols"]):
                    seat = (hall_index, row_index, col_index)
                    if seat in hall["blockedSeats"]:
                        row.append("BLOCKED")
                    else:
                        row.append(assigned_by_seat.get(seat))
                seating.append(row)

            output_halls.append({
                "hallName": hall["hallName"],
                "rows": hall["rows"],
                "cols": hall["cols"],
                "seating": seating,
            })

        return {
            "success": True,
            "message": "Seating arrangement generated successfully.",
            "constraintsRelaxed": False,
            "warnings": [],
            "halls": output_halls,
        }

    def _failure(self, halls, students, seats, reason, details):
        return {
            "success": False,
            "message": NO_SOLUTION_MESSAGE,
            "failureReason": reason,
            "failureDetails": details,
            "diagnostics": {
                "students": len(students),
                "availableSeats": len(seats),
                "shortfall": max(0, len(students) - len(seats)),
            },
            "constraintsRelaxed": False,
            "warnings": [],
            "trace": [
                f"Loaded {len(students)} students.",
                f"Computed {len(seats)} usable seats.",
                f"Search stopped: {reason}.",
            ],
            "metrics": {
                "assignments": 0,
                "backtracks": 0,
                "pruned": 0,
                "recursiveCalls": 0,
                "mrvSelections": 0,
                "solveTime": 0,
            },
            "confidence": 0,
            "quality": {
                "hallBalance": 0,
                "utilization": 0,
                "separation": 0,
                "compliance": 100,
            },
            "utilityScore": 0,
            "utilityBreakdown": {
                "hallBalance": 0,
                "subjectSeparation": 0,
                "seatUtilization": 0,
                "unusedSeatEfficiency": 0,
            },
            "arrangements": [],
            "halls": self._empty_halls(halls),
        }

    def _empty_halls(self, halls):
        output_halls = []
        for hall_index, hall in enumerate(halls):
            seating = []
            for row_index in range(hall["rows"]):
                row = []
                for col_index in range(hall["cols"]):
                    seat = (hall_index, row_index, col_index)
                    row.append("BLOCKED" if seat in hall["blockedSeats"] else None)
                seating.append(row)

            output_halls.append({
                "hallName": hall["hallName"],
                "rows": hall["rows"],
                "cols": hall["cols"],
                "seating": seating,
            })
        return output_halls

    def _evaluate(self, output_halls, normalized_halls, same_subject_mode, include_diagonal):
        usable_capacity = sum(
            hall["rows"] * hall["cols"] - len(hall["blockedSeats"])
            for hall in normalized_halls
        )
        occupied_counts = [
            sum(1 for row in hall["seating"] for seat in row if isinstance(seat, dict))
            for hall in output_halls
        ]
        total_occupied = sum(occupied_counts)
        utilization = self._percentage(total_occupied, usable_capacity)

        active_counts = [count for count in occupied_counts if count > 0]
        if len(active_counts) <= 1:
            hall_balance = 100
        else:
            average = sum(active_counts) / len(active_counts)
            deviation = sum(abs(count - average) for count in active_counts) / len(active_counts)
            hall_balance = round(max(0, 100 - deviation / max(1, average) * 100), 1)

        conflict_pairs = 0
        comparable_pairs = 0
        for hall_index, hall in enumerate(output_halls):
            seat_lookup = {}
            for row_index, row in enumerate(hall["seating"]):
                for col_index, student in enumerate(row):
                    if isinstance(student, dict):
                        seat_lookup[(hall_index, row_index, col_index)] = student
            for seat, student in seat_lookup.items():
                for neighbor in self.get_neighboring_seats(seat, same_subject_mode, include_diagonal):
                    if neighbor <= seat or neighbor not in seat_lookup:
                        continue
                    comparable_pairs += 1
                    if seat_lookup[neighbor].get("Branch") == student.get("Branch"):
                        conflict_pairs += 1

        separation = 100 if comparable_pairs == 0 else round((1 - conflict_pairs / comparable_pairs) * 100, 1)
        compliance = 100
        unused_efficiency = utilization
        breakdown = {
            "hallBalance": round(hall_balance * 0.40, 1),
            "subjectSeparation": round(separation * 0.30, 1),
            "seatUtilization": round(utilization * 0.20, 1),
            "unusedSeatEfficiency": round(unused_efficiency * 0.10, 1),
        }
        utility_score = round(sum(breakdown.values()), 1)
        confidence = round(
            hall_balance * 0.25 + utilization * 0.20 + separation * 0.35 + compliance * 0.20,
            1,
        )
        return {
            "confidence": confidence,
            "quality": {
                "hallBalance": hall_balance,
                "utilization": utilization,
                "separation": separation,
                "compliance": compliance,
            },
            "utilityScore": utility_score,
            "utilityBreakdown": breakdown,
        }

    def _arrangement_signature(self, halls):
        return tuple(
            seat.get("RollNo") if isinstance(seat, dict) else seat
            for hall in halls
            for row in hall["seating"]
            for seat in row
        )

    def _percentage(self, value, total):
        if total <= 0:
            return 0
        return round(value / total * 100, 1)

    def _student_by_id(self, variables, student_id):
        for variable in variables:
            if variable["id"] == student_id:
                return variable
        return {}

    def _public_student(self, variable):
        return {
            "RollNo": variable["RollNo"],
            "Name": variable["Name"],
            "Branch": variable["Branch"],
        }

    def _parse_blocked_seats(self, value, hall_index, rows, cols):
        blocked = set()
        if not value:
            return blocked

        raw_items = value if isinstance(value, list) else str(value).split(",")
        for raw_item in raw_items:
            item = str(raw_item).strip().upper()
            if not item:
                continue

            row_index, col_index = self._parse_position(item)
            if row_index is None or col_index is None:
                continue

            if 0 <= row_index < rows and 0 <= col_index < cols:
                blocked.add((hall_index, row_index, col_index))

        return blocked

    def _parse_position(self, value):
        patterns = [
            r"^R(\d+)C(\d+)$",
            r"^(\d+)[-:](\d+)$",
            r"^(\d+),(\d+)$",
        ]

        for pattern in patterns:
            match = re.match(pattern, value)
            if match:
                return int(match.group(1)) - 1, int(match.group(2)) - 1

        letter_row = re.match(r"^([A-Z])(\d+)$", value)
        if letter_row:
            return ord(letter_row.group(1)) - ord("A"), int(letter_row.group(2)) - 1

        column_only = re.match(r"^C(\d+)$", value)
        if column_only:
            return 0, int(column_only.group(1)) - 1

        return None, None
