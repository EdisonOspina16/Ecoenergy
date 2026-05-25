"use client";

import React from "react";
import styles from "../../styles/login.module.css";
import { useLogin } from "../../hooks/useLogin";

export default function Login() {
  const {
    correo,
    contrasena,
    error,
    loading,
    setCorreo,
    setContrasena,
    resetError,
    submit,
  } = useLogin();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submit();
  };

  return (
    <>
      <header className={styles.header}>
        {"ECOENERGY"}
        <span style={{ color: "#FFD700", marginLeft: "10px" }}>
          <i className="fas fa-lightbulb"></i>
        </span>
      </header>

      <div className={styles.container}>
        <div className={`${styles.decoration} ${styles.decoration1}`}></div>
        <div className={`${styles.decoration} ${styles.decoration2}`}></div>

        <div className={styles.icono}>
          <i
            className="fas fa-lightbulb"
            style={{ color: "#FFD700", fontSize: "42px" }}
          ></i>
        </div>

        <h1>INICIAR SESIÓN</h1>
        <p>Inicia sesión para continuar con tu experiencia sostenible</p>

        {error && (
          <div
            style={{
              color: "#ff4444",
              backgroundColor: "#ffe6e6",
              padding: "10px",
              borderRadius: "5px",
              marginBottom: "20px",
              textAlign: "center",
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className={styles.inputGroup}>
            <i className={`fas fa-envelope ${styles.inputIcon}`}></i>
            <input
              type="email"
              placeholder="Tu correo electrónico"
              required
              className={styles.iconInput}
              value={correo}
              onChange={(e) => {
                resetError();
                setCorreo(e.target.value);
              }}
            />
          </div>

          <div className={styles.inputGroup}>
            <i className={`fas fa-lock ${styles.inputIcon}`}></i>
            <input
              type="password"
              placeholder="Tu contrasena"
              required
              className={styles.iconInput}
              value={contrasena}
              onChange={(e) => {
                resetError();
                setContrasena(e.target.value);
              }}
            />
          </div>

          <button type="submit" disabled={loading}>
            <i
              className="fas fa-sign-in-alt"
              style={{ marginRight: "8px" }}
            ></i>
            {loading ? "INGRESANDO..." : "INGRESAR"}
          </button>
        </form>

        <div className={styles.linksContainer}>
          <a href="/registro">
            <i className="fas fa-user-plus" style={{ marginRight: "5px" }}></i>
            {" ¿No tienes cuenta? Regístrate"}
          </a>

          <a href="/recuperar">
            <i className="fas fa-key" style={{ marginRight: "5px" }}></i>
            {" ¿Olvidaste tu contrasena?"}
          </a>
        </div>
      </div>
    </>
  );
}
