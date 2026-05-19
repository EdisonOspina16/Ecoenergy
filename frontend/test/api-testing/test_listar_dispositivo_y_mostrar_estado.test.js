/**
 * Pruebas Unitarias - Frontend
 * Función: listarDispositivos
 * Framework: Vitest + Chai (fluent assertions)
 */

import { describe, test } from "vitest";
import { expect } from "chai";

async function listarDispositivos(fetchFn) {
  let dispositivos = [];
  let errorMsg = null;

  try {
    const response = await fetchFn("/api/dispositivos");

    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        dispositivos = data.dispositivos.map((d) => ({
          nombre: d.nombre,
          consumo: d.consumo,
          estado: d.estado,
        }));
      }
    } else {
      throw new Error("Error del servidor");
    }
  } catch (e) { //NOSONAR
    errorMsg = "Error al cargar";
    dispositivos = [];
  }

  return { dispositivos, errorMsg };
}

describe("listarDispositivos", () => {
  test("C1 - Data válida: retorna lista mapeada de dispositivos", async () => {
    const fetchFn = async () => ({
      ok: true,
      json: async () => ({
        success: true,
        dispositivos: [
          { nombre: "Lámpara", consumo: 60, estado: "encendido" },
          { nombre: "Ventilador", consumo: 100, estado: "apagado" },
        ],
      }),
    });

    const resultado = await listarDispositivos(fetchFn);

    expect(Array.isArray(resultado.dispositivos)).to.equal(true);
    expect(resultado.dispositivos.length).to.equal(2);
    expect(resultado.dispositivos[0].nombre).to.equal("Lámpara");
    expect(resultado.errorMsg).to.be.null;
  });

  test("C2 - success=false: retorna lista vacía", async () => {
    const fetchFn = async () => ({
      ok: true,
      json: async () => ({ success: false, dispositivos: [] }),
    });

    const resultado = await listarDispositivos(fetchFn);

    expect(resultado.dispositivos).to.deep.equal([]);
    expect(resultado.errorMsg).to.be.null;
  });

  test("C3 - Servidor retorna 404/500: lista vacía con error", async () => {
    const fetchFn = async () => ({ ok: false, status: 404 });

    const resultado = await listarDispositivos(fetchFn);

    expect(resultado.dispositivos).to.deep.equal([]);
    expect(resultado.errorMsg).to.equal("Error al cargar");
  });

  test("C4 - Error de red: fetch lanza excepción, lista vacía", async () => {
    const fetchFn = async () => {
      throw new TypeError("Failed to fetch");
    };

    const resultado = await listarDispositivos(fetchFn);

    expect(resultado.dispositivos).to.deep.equal([]);
    expect(resultado.errorMsg).to.equal("Error al cargar");
  });
});