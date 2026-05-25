describe("UI | Inicio de sesión", () => {
  beforeEach(() => {
    cy.mockApi({ authenticated: false });
  });

  it("muestra error con credenciales inválidas", () => {
    cy.mockApi({ authenticated: false, loginSuccess: false });
    cy.visit("/login");
    cy.fillControlledInput('form input[type="email"]', "mal@test.com");
    cy.fillControlledInput('form input[type="password"]', "wrong");
    cy.contains("form button", /ingresar/i).click();

    cy.wait("@apiLogin");
    cy.contains(/credenciales inválidas/i).should("be.visible");
  });

  it("redirige a /home tras login exitoso", () => {
    cy.mockApi({ authenticated: true });
    cy.loginByUi();
    cy.url().should("include", "/home");
    cy.contains(/Resumen de Consumo/i).should("be.visible");
  });
});
