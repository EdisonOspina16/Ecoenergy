describe("UI | Cierre de sesión", () => {
  const api = () => Cypress.env("apiUrl") || "http://localhost:5000";

  beforeEach(() => {
    cy.loadPerfilFixtures();
  });

  it("cierra sesión desde el dashboard y vuelve al login", () => {
    cy.intercept("GET", `${api()}/perfil`, {
      statusCode: 200,
      body: {
        success: true,
        hogar: { nombre_hogar: "Casa", direccion: "Calle 1" },
        dispositivos: [],
        usuario: { nombre: "Admin", correo: "admin@test.com" },
      },
    }).as("dashboardPerfil");
    cy.intercept("POST", `${api()}/logout`, {
      statusCode: 200,
      body: { success: true },
    }).as("apiLogoutDashboard");

    cy.visit("/dashboard");
    cy.wait("@dashboardPerfil");
    cy.contains(/hola,\s*admin/i, { timeout: 15000 }).should("be.visible");

    cy.contains("button", /cerrar sesión/i).click({ force: true });
    cy.wait("@apiLogoutDashboard");
    cy.url().should("include", "/login");
  });
});
