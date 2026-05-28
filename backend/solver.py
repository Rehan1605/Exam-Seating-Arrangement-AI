import random
import re
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
        same_subject_mode = constraints.get("sameSubjectHandling", "prevent-adjacent")
        include_diagonal = bool(constraints.get("includeDiagonalAdjacency", False))

        normalized_halls = self._normalize_halls(halls)
        variables = self._build_variables(students, shuffle)
        seats = self._build_domains(normalized_halls)

        if len(variables) > len(seats):
            return self._failure(normalized_halls)

        domains = {variable["id"]: list(seats) for variable in variables}
        if shuffle:
            for domain in domains.values():
                random.shuffle(domain)

        assignment = self._backtrack(
            variables=variables,
            domains=domains,
            assignment={},
            same_subject_mode=same_subject_mode,
            include_diagonal=include_diagonal,
        )

        if assignment is None:
            return self._failure(normalized_halls)

        return self._build_output(normalized_halls, variables, assignment)

    def _backtrack(self, variables, domains, assignment, same_subject_mode, include_diagonal):
        """Recursive backtracking search over student-seat assignments."""
        if len(assignment) == len(variables):
            return assignment

        variable = self._select_unassigned_variable_mrv(variables, domains, assignment)
        if variable is None:
            return None

        for seat in list(domains[variable["id"]]):
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

            domains[variable_id] = [seat for seat in domains[variable_id] if seat != assigned_seat]

            if self.check_subject_conflict(assigned_variable, variable, same_subject_mode):
                blocked_neighbors = set(self.get_neighboring_seats(
                    assigned_seat,
                    mode=same_subject_mode,
                    include_diagonal=include_diagonal,
                ))
                domains[variable_id] = [seat for seat in domains[variable_id] if seat not in blocked_neighbors]

            if not domains[variable_id]:
                return None

        return domains

    def _select_unassigned_variable_mrv(self, variables, domains, assignment):
        """MRV heuristic: pick the unassigned student with the smallest domain."""
        unassigned = [variable for variable in variables if variable["id"] not in assignment]
        if not unassigned:
            return None
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

    def _failure(self, halls):
        return {
            "success": False,
            "message": NO_SOLUTION_MESSAGE,
            "constraintsRelaxed": False,
            "warnings": [],
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
