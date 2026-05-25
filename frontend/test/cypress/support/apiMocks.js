/** Interceptores API (solo localhost:5000, no rutas de Next.js). */

const api = () => `${Cypress.env("apiUrl") || "http://localhost:5000"}`;

const HOGAR_FIXTURE = {
  nombre_hogar: "Casa Cypress",
  direccion: "Calle 50 #45-32, Medellín",
};

const DISPOSITIVOS_PERFIL = [
  { id: 1, name: "Lámpara Sala", icon: "lightbulb", connected: true },
  { id: 2, name: "Televisor", icon: "tv", connected: false },
];

function buildPerfilBody(hogar, dispositivos) {
  return {
    success: true,
    hogar: hogar || null,
    dispositivos: dispositivos || [],
  };
}

function buildHomeApis() {
  return {
    home: {
      total_consumo_kwh: 12.5,
      potencia_actual_kw: 0.85,
    },
    consumo: {
      success: true,
      datos: [
        { consumo: 2.1, periodo: "08:00" },
        { consumo: 3.4, periodo: "12:00" },
      ],
    },
    recomendacion: {
      success: true,
      recomendaciones: [
        {
          titulo: "Apaga standby",
          descripcion: "Desconecta cargadores sin uso.",
        },
      ],
      ahorro_financiero: "$5.000",
      impacto_ambiental: "2 kg CO₂",
      indicador_didactico: "Buen hábito",
    },
    dispositivos: {
      success: true,
      dispositivos: [
        {
          nombre: "Lámpara Sala",
          consumo: 1.25,
          watts: 60,
          estado: "Encendido",
        },
        {
          nombre: "Televisor",
          consumo: 0.5,
          watts: 120,
          estado: "Apagado",
        },
      ],
    },
  };
}

Cypress.Commands.add("mockApi", (options = {}) => {
  const {
    authenticated = true,
    hogar = null,
    dispositivosPerfil = [],
    loginRedirect = "/home",
  } = options;
  const loginSuccess = options.loginSuccess ?? authenticated;

  const base = api();
  const homeData = buildHomeApis();

  if (loginSuccess) {
    cy.intercept("POST", `${base}/login`, {
      statusCode: 200,
      body: {
        success: true,
        message: "Inicio de sesión exitoso",
        redirect: loginRedirect,
        usuario: { nombre: "Usuario", correo: "cypress@test.ecoenergy", id: 1 },
      },
    }).as("apiLogin");
  } else {
    cy.intercept("POST", `${base}/login`, {
      statusCode: 401,
      body: { error: "Credenciales inválidas" },
    }).as("apiLogin");
  }

  cy.intercept("POST", `${base}/logout`, {
    statusCode: 200,
    body: { success: true, message: "Sesión cerrada exitosamente" },
  }).as("apiLogout");

  cy.intercept("POST", `${base}/recuperar`, {
    statusCode: 200,
    body: {
      message: "contrasena actualizada correctamente",
      redirect: "/login",
    },
  }).as("apiRecuperar");

  cy.intercept("POST", `${base}/subscribe`, {
    statusCode: 200,
    body: { message: "Correo enviado correctamente" },
  }).as("apiSubscribe");

  const perfilStatus = authenticated ? 200 : 401;
  const perfilBody = authenticated
    ? buildPerfilBody(hogar, dispositivosPerfil)
    : { success: false, error: "Debes iniciar sesión" };

  cy.intercept("GET", `${base}/perfil`, {
    statusCode: perfilStatus,
    body: perfilBody,
  }).as("apiGetPerfil");

  cy.intercept("POST", `${base}/perfil`, (req) => {
    const body = req.body;
    if (body && body.deviceId) {
      req.reply({
        statusCode: 201,
        body: {
          success: true,
          message: "Dispositivo registrado exitosamente",
          dispositivo: {
            id: 99,
            name: body.nickname,
            icon: "lightbulb",
            connected: false,
          },
        },
      });
      return;
    }
    req.reply({
      statusCode: 200,
      body: {
        success: true,
        message: "Perfil creado exitosamente",
        hogar: {
          nombre_hogar: body.nombre_hogar,
          direccion: body.address,
        },
      },
    });
  }).as("apiPostPerfil");

  cy.intercept("DELETE", `${base}/perfil/dispositivo/*`, {
    statusCode: 200,
    body: { success: true, message: "Dispositivo eliminado exitosamente" },
  }).as("apiDeleteDispositivo");

  cy.intercept("PUT", `${base}/perfil/dispositivo/*/estado`, {
    statusCode: 200,
    body: { success: true, message: "Dispositivo encendido correctamente" },
  }).as("apiEstadoDispositivo");

  cy.intercept("GET", `${base}/home`, {
    statusCode: authenticated ? 200 : 401,
    body: homeData.home,
  }).as("apiHome");

  cy.intercept("GET", `${base}/consumo-historico*`, {
    statusCode: authenticated ? 200 : 401,
    body: homeData.consumo,
  }).as("apiConsumo");

  cy.intercept("GET", `${base}/recomendacion-diaria`, {
    statusCode: authenticated ? 200 : 401,
    body: homeData.recomendacion,
  }).as("apiRecomendacion");

  cy.intercept("GET", `${base}/dispositivos`, {
    statusCode: authenticated ? 200 : 401,
    body: homeData.dispositivos,
  }).as("apiDispositivos");
});

/** Rellena inputs controlados por React sin encadenar tras re-render. */
Cypress.Commands.add("fillControlledInput", (selector, value) => {
  cy.get(selector).scrollIntoView();
  cy.get(selector).should("be.visible");
  cy.get(selector).clear();
  cy.get(selector).type(value);
});

Cypress.Commands.add("loginByUi", (email, password) => {
  const correo = email || Cypress.env("testEmail");
  const contrasena = password || Cypress.env("testPassword");

  cy.visit("/login");
  cy.contains("h1", /INICIAR SESIÓN/i).should("be.visible");
  cy.fillControlledInput('form input[type="email"]', correo);
  cy.fillControlledInput('form input[type="password"]', contrasena);
  cy.contains("form button", /ingresar/i).click();
  cy.wait("@apiLogin", { timeout: 20000 });
});

Cypress.Commands.add("loadPerfilFixtures", () => {
  cy.mockApi({
    authenticated: true,
    hogar: {
      nombre_hogar: HOGAR_FIXTURE.nombre_hogar,
      direccion: HOGAR_FIXTURE.direccion,
    },
    dispositivosPerfil: DISPOSITIVOS_PERFIL,
  });
});
