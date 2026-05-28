function PageContainer({ eyebrow, title, description, children, actions }) {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <div>
          {eyebrow && <p className="eyebrow">{eyebrow}</p>}
          <h1>{title}</h1>
          {description && <p>{description}</p>}
        </div>
        {actions && <div className="page-actions">{actions}</div>}
      </section>
      {children}
    </main>
  )
}

export default PageContainer
