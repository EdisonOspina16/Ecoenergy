"use client";

import React, { useState, useEffect } from "react";
import styles from "../../styles/login.module.css";

interface Usuario {
  nombre?: string;
  correo?: string;
  fecha_registro?: string;
  [key: string]: any;
}

export default function Dashboard() {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // Verificar si hay usuario logueado
    fetch("http://localhost:5000/perfil", {
      credentials: "include"
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error("No hay sesión activa");
      })
      .then(data => {
        setUsuario(data.usuario);
        setLoading(false);
      })
      .catch(error => {
        console.log("Usuario no autenticado");
        setError("Debes iniciar sesión para acceder al dashboard");
        setLoading(false);
      });
  }, []);

  const handleLogout = async () => {
    try {
      const response = await fetch("http://localhost:5000/logout", {
        method: "POST",
        credentials: "include"
      });

      if (response.ok) {
        window.location.href = "/login";
      }
    } catch (error) {
      console.error("Error al cerrar sesión:", error);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div style={{ textAlign: "center", padding: "50px" }}>
          <i className="fas fa-spinner fa-spin" style={{ fontSize: "48px", color: "#FFD700" }}></i>
          <p>Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div style={{ 
          color: "#ff4444", 
          backgroundColor: "#ffe6e6", 
          padding: "20px", 
          borderRadius: "10px", 
          marginBottom: "20px",
          textAlign: "center"
        }}>
          <i className="fas fa-exclamation-triangle" style={{ marginRight: "10px" }}></i>
          {error}
        </div>
        <div style={{ textAlign: "center" }}>
          <a href="/login" style={{ 
            background: "#FFD700", 
            color: "#000", 
            padding: "12px 24px", 
            borderRadius: "5px", 
            textDecoration: "none",
            fontWeight: "bold"
          }}>
            <i className="fas fa-sign-in-alt" style={{ marginRight: "8px" }}></i>
            {" Iniciar Sesión"}
          </a>
        </div>
      </div>
    );
  }

  return (
    <>
      <header className={styles.header}>
        {"ECOENERGY DASHBOARD"}
        <span style={{ color: "#FFD700", marginLeft: "10px" }}>
          <i className="fas fa-lightbulb"></i>
        </span>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "20px" }}>
          <span>Hola, {usuario?.nombre}</span>
          <button 
            onClick={handleLogout}
            style={{
              background: "transparent",
              border: "1px solid #FFD700",
              color: "#FFD700",
              padding: "8px 16px",
              borderRadius: "5px",
              cursor: "pointer"
            }}
          >
            <i className="fas fa-sign-out-alt" style={{ marginRight: "5px" }}></i>
            {" Cerrar Sesión"}
          </button>
        </div>
      </header>

      <div className={styles.container}>
        <div className={`${styles.decoration} ${styles.decoration1}`}></div>
        <div className={`${styles.decoration} ${styles.decoration2}`}></div>

        <div className={styles.icono}>
          <i
            className="fas fa-tachometer-alt"
            style={{ color: "#FFD700", fontSize: "42px" }}
          ></i>
        </div>

        <h1>DASHBOARD</h1>
        <p>Bienvenido a tu panel de control de EcoEnergy</p>

        <div style={{ 
          backgroundColor: "#f0f8ff", 
          padding: "20px", 
          borderRadius: "10px", 
          marginBottom: "20px",
          textAlign: "center"
        }}>
          <h3>Información del Usuario</h3>
          <p><strong>Nombre:</strong> {usuario?.nombre}</p>
          <p><strong>Correo:</strong> {usuario?.correo}</p>
          <p><strong>Fecha de registro:</strong> {usuario?.fecha_registro}</p>
        </div>

        <div style={{ 
          backgroundColor: "#e6ffe6", 
          padding: "20px", 
          borderRadius: "10px", 
          marginBottom: "20px",
          textAlign: "center"
        }}>
          <h3>Funcionalidades Disponibles</h3>
          <p>Aquí podrás gestionar tus dispositivos de energía, ver estadísticas de consumo y más.</p>
          <p style={{ color: "#666", fontSize: "14px" }}>
            <i className="fas fa-info-circle" style={{ marginRight: "5px" }}></i>
            {" Las funcionalidades adicionales se implementarán próximamente."}
          </p>
        </div>

        <div style={{ textAlign: "center" }}>
          <a href="/" style={{ 
            background: "transparent", 
            color: "#FFD700", 
            border: "2px solid #FFD700", 
            padding: "10px 22px", 
            borderRadius: "5px", 
            textDecoration: "none",
            fontWeight: "bold",
            marginRight: "10px"
          }}>
            <i className="fas fa-home" style={{ marginRight: "8px" }}></i>
            {" Volver al Inicio"}
          </a>
        </div>
      </div>
    </>
  );
}
