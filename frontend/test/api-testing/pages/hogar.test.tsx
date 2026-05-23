import React from "react";
import { describe, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import HomePage from "@/app/home/page";
import * as useDispositivosHooks from "@/hooks/useDispositivos";
import { expect } from "chai";

// Mockeamos la location global ya que hay un globalThis.location para la validacion oauth en la UI
beforeEach(() => {
  vi.clearAllMocks();
  Object.defineProperty(globalThis, "location", {
    value: { href: "" },
    writable: true,
  });
});

describe("Página: Dashboard Hogar", () => {
  const mockCargarDispositivos = vi.fn();

  beforeEach(() => {
    vi.spyOn(useDispositivosHooks, "cargarDispositivos").mockImplementation(
      ({ setDevices, setLoadingDevices }) => {
        setDevices([
          {
            nombre: "Nevera Inteligente",
            consumo: 0.12,
            watts: 180,
            estado: "Encendido",
          },
        ]);
        setLoadingDevices(false);
        return Promise.resolve();
      },
    );

    // Mockeamos el fetch global (consumo historico y consumo)
    globalThis.fetch = vi.fn((url: string | URL | Request) => {
      const urlStr = url.toString();
      if (urlStr.includes("consumo-historico")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ success: true, datos: [] }),
        } as Response);
      }
      if (urlStr.includes("perfil")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            success: true,
            hogar: { nombre_hogar: "Mi Hogar Mock", direccion: "123 Mock" },
          }),
        } as Response);
      }
      if (urlStr.includes("/home")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            success: true,
            total_consumo_kwh: 4.2,
            potencia_actual_kw: 0.85,
          }),
        } as Response);
      }
      if (urlStr.includes("recomendacion-diaria")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            success: true,
            recomendaciones: [
              { recomendacion: "Apaga la luz", esAlerta: false },
            ],
          }),
        } as Response);
      }
      // Respuesta default ok para evitar bugs de red en el DOM artificial
      return Promise.resolve({
        ok: true,
        json: async () => ({ success: true }),
      } as Response);
    });
  });

  it("debería renderizar la UI base y mostrar estado de carga global inicialmente (Render)", async () => {
    render(<HomePage />);

    // Componente principal de nombre
    expect(screen.queryByText("ECOENERGY")).to.not.equal(null);

    // La carga de dispositivos inicial va con mock así que "Nevera" debería estar mapeada
    await waitFor(() => {
      expect(screen.queryByText("Nevera Inteligente")).to.not.equal(null);
    });

    // Verifica la interpolación de state
    expect(screen.queryByText("0.85")).to.not.equal(null);
    expect(screen.queryByText("0.18 kW · 0.120 kWh (24 h)")).to.not.equal(null);
  });

  it("debería llamar a los servicios correspondientes on mount (Verify Fetch Spies)", async () => {
    render(<HomePage />);

    await waitFor(() => {
      // Debe haber consultado historial de consumo
      const fetchCalls = vi.mocked(globalThis.fetch).mock.calls;
      expect(fetchCalls.length).to.be.greaterThan(0);
      const consumoHistoricoCall = fetchCalls.find((call) =>
        String(call[0]).includes("consumo-historico"),
      );
      expect(consumoHistoricoCall).to.not.equal(undefined);
      expect(consumoHistoricoCall![1]).to.not.equal(undefined);

      // Debe haber mandado llamar cargarDispositivos al iniciar
      expect(mockCargarDispositivos.mock.calls.length).to.equal(0); // Wait, it triggers the spy implementation inline bypassing mock.
      expect(
        vi.mocked(useDispositivosHooks.cargarDispositivos).mock.calls.length,
      ).to.be.greaterThan(0);
    });
  });

  it("debería capturar el error de login e ir al auth si tira 401", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 401,
    } as Response);

    render(<HomePage />);

    await waitFor(() => {
      expect(globalThis.location.href).to.equal("/login");
    });
  });
});
