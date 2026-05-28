function SeatingGrid({ hall }) {
  if (!hall) {
    return null
  }

  return (
    <div className="seating-grid" style={{ gridTemplateColumns: `repeat(${hall.cols}, minmax(86px, 1fr))` }}>
      {hall.seating.flatMap((row, rowIndex) => row.map((seat, columnIndex) => {
        const isBlocked = seat === 'BLOCKED'
        const isEmpty = seat === null
        const seatClass = isBlocked ? 'blocked' : isEmpty ? 'empty' : ''

        return (
          <div className={`seat ${seatClass}`} key={`${rowIndex}-${columnIndex}`}>
            <small>R{rowIndex + 1} C{columnIndex + 1}</small>
            {isBlocked && <strong>Blocked</strong>}
            {isEmpty && <strong>Empty</strong>}
            {!isBlocked && !isEmpty && (
              <>
                <strong>{seat.RollNo}</strong>
                <span>{seat.Name}</span>
                <em>{seat.Branch}</em>
              </>
            )}
          </div>
        )
      }))}
    </div>
  )
}

export default SeatingGrid
