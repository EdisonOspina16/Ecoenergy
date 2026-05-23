import { fetchDispositivos } from "../lib/api/dispositivos";

export type Device = {
  nombre: string;
  consumo?: number;
  estado?: string;
  [key: string]: any;
};

export type CargarDispositivosSetters = {
  setDevices: (devices: Device[]) => void;
  setLoadingDevices: (loading: boolean) => void;
  /** Si es true, no muestra estado de carga (útil en actualización periódica). */
  silent?: boolean;
};

export async function cargarDispositivos({
  setDevices,
  setLoadingDevices,
  silent = false,
}: CargarDispositivosSetters): Promise<void> {
  try {
    if (!silent) {
      setLoadingDevices(true);
    }
    const result = await fetchDispositivos();
    if (result.ok) {
      const dispositivosMapeados: Device[] = result.dispositivos.map((d) => ({
        nombre: d.nombre,
        consumo: Number(d.consumo) || 0,
        watts: Number(d.watts) || 0,
        estado: d.estado || "Desconocido",
      }));
      setDevices(dispositivosMapeados);
    } else {
      setDevices([]);
    }
  } catch (error) {
    console.error("Error al cargar dispositivos:", error);
    setDevices([]);
  } finally {
    if (!silent) {
      setLoadingDevices(false);
    }
  }
}
