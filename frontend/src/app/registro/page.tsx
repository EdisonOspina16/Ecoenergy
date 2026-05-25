"use client";

import React, { useState } from "react";
import styles from "../../styles/login.module.css";
import { registrarUsuario as registrarUsuarioFn } from "../../hooks/useRegistro";

export default function Registro() {
  const [nombre, setNombre] = useState("");
  const [apellidos, setApellidos] = useState("");
  const [correo, setCorreo] = useState("");
  const [contrasena, setcontrasena] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await registrarUsuarioFn(nombre, apellidos, correo, contrasena, {
      setLoading,
      setError,
    });
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
            className="fas fa-user-plus"
            style={{ color: "#FFD700", fontSize: "42px" }}
          ></i>
        </div>

        <h1>REGISTRO</h1>
        <p>Completa tus datos básicos para crear tu cuenta</p>

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
            <i className={`fas fa-user ${styles.inputIcon}`}></i>
            <input
              type="text"
              placeholder="Tu nombre"
              required
              className={styles.iconInput}
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
            />
          </div>

          <div className={styles.inputGroup}>
            <i className={`fas fa-user ${styles.inputIcon}`}></i>
            <input
              type="text"
              placeholder="Tus apellidos"
              required
              className={styles.iconInput}
              value={apellidos}
              onChange={(e) => setApellidos(e.target.value)}
            />
          </div>

          <div className={styles.inputGroup}>
            <i className={`fas fa-envelope ${styles.inputIcon}`}></i>
            <input
              type="email"
              placeholder="Tu correo electrónico"
              required
              className={styles.iconInput}
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
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
              onChange={(e) => setcontrasena(e.target.value)}
            />
          </div>

          <button type="submit" disabled={loading}>
            <i className="fas fa-check" style={{ marginRight: "8px" }}></i>
            {loading ? "REGISTRANDO..." : "COMPLETAR REGISTRO"}
          </button>
        </form>

        <div className={styles.linksContainer}>
          <a href="/login">
            <i
              className="fas fa-sign-in-alt"
              style={{ marginRight: "5px" }}
            ></i>
            {" ¿Ya tienes cuenta? Inicia sesión"}
          </a>
        </div>
      </div>
    </>
  );
}
