'use client';

import React, { useState, useEffect } from 'react';
import { cargarDispositivos } from '../../hooks/useDispositivos';

type Device = {
  nombre: string;
  consumo?: number;
  estado?: string;
  [key: string]: any;
};

type ChartPoint = {
  consumo: number;
  periodo?: string;
  [key: string]: any;
};

export default function Home() {
  const [timeRange, setTimeRange] = useState<'day' | 'week' | 'month'>('day');
  const [showUserMenu, setShowUserMenu] = useState<boolean>(false);
  const [homeName, setHomeName] = useState<string>('Mi Hogar');
  const [address, setAddress] = useState<string>('Sin dirección');
  const [totalConsumo, setTotalConsumo] = useState<number>(0);
  const [potenciaActualKw, setPotenciaActualKw] = useState<number>(0);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [chartData, setChartData] = useState<ChartPoint[]>([]);
  const [chartLoading, setChartLoading] = useState<boolean>(false);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loadingDevices, setLoadingDevices] = useState<boolean>(true);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState<boolean>(false);
  const [savingData, setSavingData] = useState<{
    ahorro_financiero: string;
    impacto_ambiental: string;
    indicador_didactico: string;
  }>({
    ahorro_financiero: '',
    impacto_ambiental: '',
    indicador_didactico: '',
  });
  const [loadingSavingData, setLoadingSavingData] = useState<boolean>(false);
  const [generandoRecomendacion, setGenerandoRecomendacion] = useState<boolean>(false);

  // Cerrar menú de usuario al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: Event) => {
      const target = event.target as HTMLElement | null;
      if (!target) return;
      if (!target.closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
    };

    if (showUserMenu) {
      document.addEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [showUserMenu]);

  // Cargar datos del perfil
  useEffect(() => {
    const cargarPerfil = async () => {
      try {
        const response = await fetch('http://localhost:5000/perfil', {
          credentials: 'include',
        });

        if (response.status === 401) {
          globalThis.location.href = '/login';
          return;
        }

        const data = await response.json();

        if (data?.success && data.hogar) {
          setHomeName(data.hogar.nombre_hogar || 'Mi Hogar');
          setAddress(data.hogar.direccion || 'Sin dirección');
        }
      } catch (error) {
        console.error('Error al cargar perfil:', error);
      }
    };

    cargarPerfil();
  }, []);

  // Cargar datos de consumo total
  useEffect(() => {
    const cargarConsumo = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/home', {
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error('Error al obtener datos de consumo');
        }

        const data = await response.json();

        if (data && typeof data.total_consumo_kwh === 'number') {
          setTotalConsumo(data.total_consumo_kwh);
          setPotenciaActualKw(
            typeof data.potencia_actual_kw === 'number' ? data.potencia_actual_kw : 0
          );
          setLastUpdate(new Date().toLocaleString('es-ES'));
        }
      } catch (error) {
        console.error('Error al cargar consumo:', error);
      } finally {
        setLoading(false);
      }
    };

    cargarConsumo();
    const interval = setInterval(cargarConsumo, 30000);
    return () => clearInterval(interval);
  }, []);

  // Cargar datos históricos para gráfico
  useEffect(() => {
    const cargarDatosHistoricos = async () => {
      try {
        setChartLoading(true);
        const response = await fetch(
          `http://localhost:5000/consumo-historico?rango=${timeRange}`,
          { credentials: 'include' }
        );

        if (!response.ok) {
          throw new Error('Error al obtener datos históricos');
        }

        const data = await response.json();

        if (data?.success && Array.isArray(data.datos)) {
          // Normalizar consumos a número
          const datos: ChartPoint[] = data.datos.map((d: any) => ({
            consumo: Number(d.consumo) || 0,
            periodo: d.periodo,
          }));
          setChartData(datos);
        } else {
          setChartData([]);
        }
      } catch (error) {
        console.error('Error al cargar datos históricos:', error);
        setChartData([]);
      } finally {
        setChartLoading(false);
      }
    };

    cargarDatosHistoricos();
  }, [timeRange]);

  // Cargar recomendación y ahorro diario (una vez por día por usuario; no se actualiza con los datos en vivo)
  useEffect(() => {
    const cargarRecomendacionDiaria = async () => {
      try {
        setLoadingRecommendations(true);
        setLoadingSavingData(true);
        const response = await fetch('http://localhost:5000/recomendacion-diaria', {
          credentials: 'include',
        });
        if (response.status === 401) {
          globalThis.location.href = '/login';
          return;
        }
        const data = await response.json();
        if (data?.success) {
          setRecommendations(Array.isArray(data.recomendaciones) ? data.recomendaciones : []);
          setSavingData({
            ahorro_financiero: data.ahorro_financiero ?? '',
            impacto_ambiental: data.impacto_ambiental ?? '',
            indicador_didactico: data.indicador_didactico ?? '',
          });
        } else {
          setRecommendations([]);
          setSavingData({ ahorro_financiero: '', impacto_ambiental: '', indicador_didactico: '' });
        }
      } catch (error) {
        console.error('Error al cargar recomendación diaria:', error);
        setRecommendations([]);
        setSavingData({ ahorro_financiero: '', impacto_ambiental: '', indicador_didactico: '' });
      } finally {
        setLoadingRecommendations(false);
        setLoadingSavingData(false);
      }
    };
    cargarRecomendacionDiaria();
  }, []);

  const generarRecomendacionHoy = async () => {
    try {
      setGenerandoRecomendacion(true);
      const response = await fetch('http://localhost:5000/recomendacion-diaria/generar', {
        method: 'POST',
        credentials: 'include',
      });
      if (response.status === 401) {
        globalThis.location.href = '/login';
        return;
      }
      const data = await response.json();
      if (data?.success) {
        setRecommendations(Array.isArray(data.recomendaciones) ? data.recomendaciones : []);
        setSavingData({
          ahorro_financiero: data.ahorro_financiero ?? '',
          impacto_ambiental: data.impacto_ambiental ?? '',
          indicador_didactico: data.indicador_didactico ?? '',
        });
      }
    } catch (error) {
      console.error('Error al generar recomendación:', error);
    } finally {
      setGenerandoRecomendacion(false);
    }
  };

  // Cargar dispositivos del usuario (actualización periódica con la simulación)
  useEffect(() => {
    cargarDispositivos({ setDevices, setLoadingDevices });
    const interval = setInterval(() => {
      cargarDispositivos({ setDevices, setLoadingDevices, silent: true });
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Render del gráfico SVG
  const renderChart = () => {
    if (chartLoading) {
      return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
          <p>Cargando datos...</p>
        </div>
      );
    }

    if (!chartData || chartData.length === 0) {
      return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
          <p>No hay datos disponibles para este período</p>
        </div>
      );
    }

    const consumos = chartData.map((d) => Number(d.consumo) || 0);
    const maxConsumo = Math.max(...consumos);
    const minConsumo = Math.min(...consumos);
    const range = maxConsumo - minConsumo || 1;

    return (
      <div style={{ padding: '1rem', height: '300px' }}>
        <svg width="100%" height="100%" viewBox="0 0 800 250">
          {[0, 1, 2, 3, 4].map((i) => (
            <g key={`grid-line-${i}`}>
              <line x1="50" y1={50 + i * 50} x2="750" y2={50 + i * 50} stroke="#E5E7EB" strokeWidth="1" />
              <text x="35" y={55 + i * 50} fill="#6B7280" fontSize="12" textAnchor="end">
                {(maxConsumo - (i * range) / 4).toFixed(1)}
              </text>
            </g>
          ))}

          <polyline
            fill="none"
            stroke="#10B981"
            strokeWidth="3"
            points={chartData
              .map((d, i) => {
                const x = 50 + i * (700 / (chartData.length - 1 || 1));
                const y = 250 - ((Number(d.consumo) - minConsumo) / range) * 200;
                return `${x},${y}`;
              })
              .join(' ')}
          />

          {chartData.map((d, i) => {
            const x = 50 + i * (700 / (chartData.length - 1 || 1));
            const y = 250 - ((Number(d.consumo) - minConsumo) / range) * 200;
            return (
              <g key={d.periodo || `point-${i}`}>
                <circle cx={x} cy={y} r="4" fill="#10B981" />
                {(chartData.length <= 12 || i % Math.ceil(chartData.length / 12) === 0) && (
                  <text x={x} y="270" fill="#6B7280" fontSize="11" textAnchor="middle">
                    {d.periodo}
                  </text>
                )}
              </g>
            );
          })}

          <text x="400" y="295" fill="#6B7280" fontSize="14" textAnchor="middle" fontWeight="600">
            {timeRange === 'day' ? 'Hora del día' : timeRange === 'week' ? 'Día de la semana' : 'Día del mes'}
          </text>
          <text x="15" y="150" fill="#6B7280" fontSize="14" textAnchor="middle" fontWeight="600" transform="rotate(-90, 15, 150)">
            Consumo (W)
          </text>
        </svg>
      </div>
    );
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#F9FAFB' }}>
      {/* Header */}
      <header
        style={{
          backgroundColor: 'white',
          borderBottom: '1px solid #E5E7EB',
          padding: '1rem 2rem',
        }}
      >
        <div
          style={{
            maxWidth: '1400px',
            margin: '0 auto',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '2rem' }}>💡</span>
            <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10B981' }}>ECOENERGY</span>
          </div>

          <nav style={{ display: 'flex', gap: '2rem' }}>
            <a
              href="/home"
              style={{
                color: '#10B981',
                textDecoration: 'none',
                fontWeight: '600',
                borderBottom: '2px solid #10B981',
                paddingBottom: '0.25rem',
              }}
            >
              Dashboard
            </a>
            <a href="/reportes" style={{ color: '#6B7280', textDecoration: 'none', fontWeight: '500' }}>
              Reports
            </a>
            <a href="/perfil" style={{ color: '#6B7280', textDecoration: 'none', fontWeight: '500' }}>
              Profile
            </a>
          </nav>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button
              style={{
                background: 'none',
                border: 'none',
                fontSize: '1.5rem',
                cursor: 'pointer',
                padding: '0.5rem',
              }}
              title="Notificaciones"
            >
              🔔
            </button>

            {/* CÍRCULO DEL PERFIL CON POPUP */}
            <div className="user-menu-container" style={{ position: 'relative' }}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                style={{
                  width: '2.5rem',
                  height: '2.5rem',
                  borderRadius: '50%',
                  backgroundImage:
                    'url("https://lh3.googleusercontent.com/aida-public/AB6AXuBqNo8fjfebe_H0I5zh8Fvrbtov-mVmsTd8fa-uhbH9zFVol60RO1YFiXKDnaYuqEvFvzosAfQHITzbl_XnkMOl7Mj6bdHGkiArUnzlzAA-283ck-z-IdS13en693-eVl1R21SdhTnNhGrfR2e4tL8qTaFtvEz782idrxUUqsPXpiFG8AecB3RWIUD8B_4nsKdkyPxIqJPn6Yp8BCLauwRCIpKZU5Iky9mRb27BtIhefRYg6c35py4fXq9x4ctwr81GnuoY51uD47cB")',
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                  border: 'none',
                  cursor: 'pointer',
                }}
              />

              {/* Menú desplegable */}
              {showUserMenu && (
                <div
                  style={{
                    position: 'absolute',
                    top: '3rem',
                    right: '0',
                    backgroundColor: 'white',
                    borderRadius: '0.5rem',
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                    border: '1px solid #E5E7EB',
                    minWidth: '200px',
                    zIndex: 50,
                  }}
                >
                  <div style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #E5E7EB' }}>
                    <p style={{ fontWeight: '600', color: '#1F2937', marginBottom: '0.25rem' }}>{homeName}</p>
                    <p style={{ fontSize: '0.875rem', color: '#6B7280' }}>{address}</p>
                  </div>
                  <div style={{ padding: '0.5rem 0' }}>
                    <a
                      href="/home"
                      style={{
                        display: 'block',
                        padding: '0.75rem 1rem',
                        color: '#10B981',
                        fontSize: '0.875rem',
                        fontWeight: '500',
                        textDecoration: 'none',
                        backgroundColor: '#F0FDF4',
                      }}
                    >
                      📊 Dashboard
                    </a>
                    <a
                      href="/reportes"
                      style={{
                        display: 'block',
                        padding: '0.75rem 1rem',
                        color: '#6B7280',
                        fontSize: '0.875rem',
                        textDecoration: 'none',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#F9FAFB')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      📈 Reportes
                    </a>
                    <a
                      href="/perfil"
                      style={{
                        display: 'block',
                        padding: '0.75rem 1rem',
                        color: '#6B7280',
                        fontSize: '0.875rem',
                        textDecoration: 'none',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#F9FAFB')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      ⚙️ Mi Perfil
                    </a>
                  </div>
                  <div style={{ borderTop: '1px solid #E5E7EB', padding: '0.5rem 0' }}>
                    <button
                      onClick={() => (globalThis.location.href = '/login')}
                      style={{
                        display: 'block',
                        width: '100%',
                        padding: '0.75rem 1rem',
                        color: '#EF4444',
                        fontSize: '0.875rem',
                        fontWeight: '500',
                        textAlign: 'left',
                        border: 'none',
                        backgroundColor: 'transparent',
                        cursor: 'pointer',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#FEF2F2')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      🚪 Cerrar Sesión
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
          {/* Left Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Resumen de Consumo */}
            <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Resumen de Consumo [{homeName}]</h1>
              {loading ? (
                <p style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#10B981' }}>Cargando...</p>
              ) : (
                <>
                  <p style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#10B981', marginBottom: '0.25rem' }}>
                    {Number(potenciaActualKw || 0).toFixed(2)}{' '}
                    <span style={{ fontSize: '1.5rem', color: '#6B7280' }}>kW</span>
                  </p>
                  <p style={{ fontSize: '0.95rem', color: '#4B5563' }}>
                    Consumo actual (dispositivos encendidos)
                  </p>
                  <p style={{ fontSize: '1rem', color: '#6B7280', marginTop: '0.75rem' }}>
                    {Number(totalConsumo || 0).toFixed(2)} kWh en las últimas 24 h
                  </p>
                </>
              )}
              <p style={{ fontSize: '0.875rem', color: '#6B7280', marginTop: '0.5rem' }}>{lastUpdate ? `Última actualización: ${lastUpdate}` : 'Actualizando...'}</p>
            </div>

            {/* Tendencia */}
            <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ fontSize: '1.125rem', fontWeight: '600' }}>Tendencia de Consumo</h2>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  {['day', 'week', 'month'].map((range) => (
                    <button
                      key={range}
                      onClick={() => setTimeRange(range as 'day' | 'week' | 'month')}
                      style={{
                        padding: '0.5rem 1rem',
                        borderRadius: '0.375rem',
                        border: '1px solid #E5E7EB',
                        backgroundColor: timeRange === range ? '#10B981' : 'white',
                        color: timeRange === range ? 'white' : '#6B7280',
                        cursor: 'pointer',
                        fontWeight: '500',
                      }}
                    >
                      {range === 'day' ? 'Día' : range === 'week' ? 'Semana' : 'Mes'}
                    </button>
                  ))}
                </div>
              </div>
              {renderChart()}
            </div>

            {/* Consumo por Dispositivo */}
            <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ fontSize: '1.125rem', fontWeight: '600' }}>Consumo por Dispositivo</h2>
                <button
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.5rem 1rem',
                    backgroundColor: '#10B981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontWeight: '500',
                  }}
                >
                  📥 Exportar a Hojas de cálculo
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {loadingDevices ? (
                  <p>Cargando dispositivos...</p>
                ) : devices.length === 0 ? (
                  <p>No hay dispositivos registrados.</p>
                ) : (
                  devices.map((device, index) => (
                    <div
                      key={`${device.nombre}-${index}`}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '1rem',
                        border: '1px solid #E5E7EB',
                        borderRadius: '0.5rem',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <span style={{ fontSize: '2rem' }}>
                          {device.nombre.toLowerCase().includes('tv') ? '📺' : device.nombre.toLowerCase().includes('nevera') ? '🧊' : device.nombre.toLowerCase().includes('aire') ? '❄️' : '🔌'}
                        </span>
                        <div>
                          <p style={{ fontWeight: '600' }}>{device.nombre}</p>
                          <p style={{ fontSize: '0.875rem', color: '#6B7280' }}>
                            {device.estado === 'Encendido'
                              ? `${((Number(device.watts) || 0) / 1000).toFixed(2)} kW · ${Number(device.consumo || 0).toFixed(4)} kWh (24 h)`
                              : `${((Number(device.watts) || 0) / 1000).toFixed(2)} kW · apagado (sin simulación activa)`}
                          </p>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div
                            style={{
                              width: '0.5rem',
                              height: '0.5rem',
                              borderRadius: '50%',
                              backgroundColor: device.estado === 'Encendido' ? '#10B981' : '#6B7280',
                            }}
                          ></div>
                          <span style={{ fontSize: '0.875rem' }}>{device.estado}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Recomendaciones (una por día; no cambian con las actualizaciones de consumo) */}
            <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h2 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>Recomendaciones del día</h2>

              {loadingRecommendations ? (
                <p>Cargando recomendaciones...</p>
              ) : recommendations.length === 0 ? (
                <div>
                  <p style={{ marginBottom: '1rem' }}>Aún no tienes recomendación para hoy. Genera una y se mantendrá en pantalla hasta mañana.</p>
                  <button
                    type="button"
                    onClick={generarRecomendacionHoy}
                    disabled={generandoRecomendacion}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: generandoRecomendacion ? '#9CA3AF' : '#10B981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '0.375rem',
                      cursor: generandoRecomendacion ? 'not-allowed' : 'pointer',
                      fontWeight: '500',
                    }}
                  >
                    {generandoRecomendacion ? 'Generando...' : 'Obtener mi recomendación de hoy'}
                  </button>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {recommendations.map((rec, index) => (
                    <div
                      key={index}
                      style={{
                        padding: '1rem',
                        backgroundColor: rec?.esAlerta ? '#FEF2F2' : '#F0FDF4',
                        border: rec?.esAlerta ? '1px solid #FCA5A5' : '1px solid #86EFAC',
                        borderRadius: '0.5rem',
                      }}
                    >
                      <p style={{ fontWeight: '600', color: rec?.esAlerta ? '#DC2626' : '#166534', marginBottom: rec?.esAlerta ? '0.5rem' : '0' }}>{rec?.recomendacion}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Ahorro (estimado del día; no cambia con las actualizaciones de consumo) */}
            <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ fontSize: '1.125rem', fontWeight: '600' }}>Tu Ahorro del día</h2>
                <button
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.5rem 1rem',
                    backgroundColor: '#10B981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontWeight: '500',
                  }}
                >
                  📥 Exportar
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ padding: '1rem', backgroundColor: '#EFF6FF', borderRadius: '0.5rem' }}>
                  <p style={{ fontSize: '0.875rem', color: '#1E40AF', marginBottom: '0.5rem' }}>Ahorro Financiero Proyectado</p>
                  <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1E3A8A' }}>
                    {loadingSavingData
                      ? 'Calculando...'
                      : savingData.ahorro_financiero || 'No disponible'}
                  </p>
                </div>
                <div style={{ padding: '1rem', backgroundColor: '#F0FDF4', borderRadius: '0.5rem' }}>
                  <p style={{ fontSize: '0.875rem', color: '#166534', marginBottom: '0.5rem' }}>Impacto Ambiental</p>
                  <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#15803D' }}>
                    {loadingSavingData
                      ? 'Calculando...'
                      : savingData.impacto_ambiental || 'No disponible'}
                  </p>
                </div>
                <div style={{ padding: '1rem', backgroundColor: '#FFFBEB', borderRadius: '0.5rem' }}>
                  <p style={{ fontSize: '0.875rem', color: '#92400E', marginBottom: '0.5rem' }}>Indicador Didáctico</p>
                  <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#78350F' }}>
                    {loadingSavingData
                      ? 'Calculando...'
                      : savingData.indicador_didactico || 'No disponible'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}