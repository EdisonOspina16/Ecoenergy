describe("Seguridad | Autenticación y acceso", () => {
  it("bloquea /perfil sin sesión (401 → login)", () => {
    const base = Cypress.env("apiUrl") || "http://localhost:5000";
    cy.mockApi({ authenticated: false });
    cy.intercept("GET", `${base}/perfil`, {
      statusCode: 401,
      body: { success: false, error: "Debes iniciar sesión" },
    }).as("perfil401");

    cy.visit("/perfil");
    cy.wait("@perfil401");
    cy.url().should("include", "/login");
  });

  it("rechaza credenciales inválidas en login", () => {
    cy.mockApi({ authenticated: false, loginSuccess: false });
    cy.visit("/login");
    cy.fillControlledInput('form input[type="email"]', "intruso@test.com");
    cy.fillControlledInput('form input[type="password"]', "hack");
    cy.contains("form button", /ingresar/i).click();
    cy.wait("@apiLogin");
    cy.url().should("include", "/login");
    cy.contains(/credenciales inválidas/i).should("be.visible");
  });

  it("no envía login con campos vacíos (validación HTML5)", () => {
    cy.mockApi({ authenticated: false });
    cy.visit("/login");
    cy.contains("form button", /ingresar/i).click();
    cy.get("@apiLogin.all").should("have.length", 0);
    cy.get('form input[type="email"]:invalid').should("exist");
  });
});
