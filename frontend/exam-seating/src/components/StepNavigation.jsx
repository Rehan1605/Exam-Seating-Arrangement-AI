import { Link } from 'react-router-dom'

function StepNavigation({ previous, next, onNext, nextLabel = 'Next Step', previousLabel = 'Previous Step', nextDisabled = false }) {
  return (
    <div className="step-navigation">
      {previous ? (
        <Link className="secondary-button arrow-button" to={previous}>
          <span aria-hidden="true">&larr;</span>
          {previousLabel}
        </Link>
      ) : <span />}
      {onNext && (
        <button className="primary-button arrow-button" type="button" onClick={onNext} disabled={nextDisabled}>
          {nextLabel}
          <span aria-hidden="true">&rarr;</span>
        </button>
      )}
      {!onNext && next && (
        <Link className="primary-button arrow-button" to={next}>
          {nextLabel}
          <span aria-hidden="true">&rarr;</span>
        </Link>
      )}
    </div>
  )
}

export default StepNavigation
