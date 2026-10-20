import { useState } from 'react'

// Input de contraseña con botón de mostrar/ocultar (ojito). Se reutiliza
// en Login (iniciar sesión y registro) y en RestablecerContrasena.
function CampoContrasena({ id, label, value, onChange, autoComplete, minLength, helpText }) {
  const [visible, setVisible] = useState(false)

  return (
    <div className="mb-3">
      <label htmlFor={id} className="form-label fw-semibold">
        {label}
      </label>
      <div className="input-group">
        <input
          id={id}
          type={visible ? 'text' : 'password'}
          className="form-control"
          value={value}
          onChange={onChange}
          required
          minLength={minLength}
          autoComplete={autoComplete}
        />
        <button
          type="button"
          className="btn btn-light border"
          onClick={() => setVisible((actual) => !actual)}
          aria-label={visible ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          tabIndex={-1}
        >
          <i className={`bi ${visible ? 'bi-eye-slash' : 'bi-eye'}`}></i>
        </button>
      </div>
      {helpText && <div className="form-text">{helpText}</div>}
    </div>
  )
}

export default CampoContrasena
