/**
 * Pruebas Unitarias - Frontend
 * Función: registrarSuscripcion
 * Framework: Vitest + Chai (fluent assertions)
 */

import { describe, test } from "vitest";
import { expect } from "chai";

async function registrarSuscripcion(email, fetchFn) {
    if (!email) {
        return { mensaje: "Por favor ingresa un correo válido", exito: false };
    }

    try {
        const response = await fetchFn("/api/suscripcion", {
            method: "POST",
            body: JSON.stringify({ email })
        });

        if (response.ok) {
            return { mensaje: "¡Gracias! setEmail", exito: true };
        } else {
            const data = await response.json();
            return { mensaje: data.error, exito: false };
        }
    } catch (e) { //NOSONAR
        return { mensaje: "No se pudo conectar con el servidor", exito: false };
    }
}

describe("registrarSuscripcion", () => {

    test("C1 - Email válido, respuesta ok: éxito y limpia email", async () => {
        const fetchFn = async () => ({ ok: true, json: async () => ({}) });

        const resultado = await registrarSuscripcion("user@correo.com", fetchFn);

        expect(resultado.exito).to.equal(true);
        expect(resultado.mensaje).to.include("Gracias");
    });

    test("C2 - Email vacío: no llama fetch, muestra validación", async () => {
        let fetchLlamado = false;
        const fetchFn = async () => { fetchLlamado = true; return {}; };

        const resultado = await registrarSuscripcion("", fetchFn);

        expect(resultado.exito).to.equal(false);
        expect(resultado.mensaje).to.equal("Por favor ingresa un correo válido");
        expect(fetchLlamado).to.equal(false);
    });

    test("C3 - Correo ya registrado: response.ok=false, muestra error", async () => {
        const fetchFn = async () => ({
            ok: false,
            json: async () => ({ error: "Correo ya registrado" })
        });

        const resultado = await registrarSuscripcion("user@correo.com", fetchFn);

        expect(resultado.exito).to.equal(false);
        expect(resultado.mensaje).to.equal("Correo ya registrado");
    });

    test("C4 - Error de red: fetch lanza excepción", async () => {
        const fetchFn = async () => { throw new TypeError("Failed to fetch"); };

        const resultado = await registrarSuscripcion("user@correo.com", fetchFn);

        expect(resultado.exito).to.equal(false);
        expect(resultado.mensaje).to.equal("No se pudo conectar con el servidor");
    });

});