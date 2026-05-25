"use client";

import React, { useState } from "react";
import styles from "../../styles/login.module.css";
import { useRecuperar } from "../../hooks/useRecuperar";

export default function Recuperar() {
  const {
    correo,
    setCorreo,
    nuevacontrasena,
    setNuevacontrasena,
    error,
    success,
    loading,
    handleSubmit
  } = useRecuperar();

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
            className="fas fa-key"
            style={{ color: "#FFD700", fontSize: "42px" }}
          ></i>
        </div>

        <h1>RECUPERAR contrasena</h1>
        <p>Ingresa tu correo y nueva contrasena</p>

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

        {success && (
          <div
            style={{
              color: "#00aa00",
              backgroundColor: "#e6ffe6",
              padding: "10px",
              borderRadius: "5px",
              marginBottom: "20px",
              textAlign: "center",
            }}
          >
            {success}
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
              onChange={(e) => setCorreo(e.target.value)}
            />
          </div>

          <div className={styles.inputGroup}>
            <i className={`fas fa-lock ${styles.inputIcon}`}></i>
            <input
              type="password"
              placeholder="Nueva contrasena"
              required
              className={styles.iconInput}
              value={nuevacontrasena}
              onChange={(e) => setNuevacontrasena(e.target.value)}
            />
          </div>

          <button type="submit" disabled={loading}>
            <i className="fas fa-save" style={{ marginRight: "8px" }}></i>
            {loading ? "ACTUALIZANDO..." : "ACTUALIZAR CONTRASENA"}
          </button>
        </form>

        <div className={styles.linksContainer}>
          <a href="/login">
            <i
              className="fas fa-sign-in-alt"
              style={{ marginRight: "5px" }}
            ></i>
            {" Volver al inicio de sesión"}
          </a>
        </div>
      </div>
    </>
  );
}
