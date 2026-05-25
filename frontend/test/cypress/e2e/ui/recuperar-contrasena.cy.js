describe("UI | Cambiar contraseña (recuperar)", () => {
  beforeEach(() => {
    cy.mockApi({ authenticated: false });
  });

  it("actualiza la contraseña y muestra mensaje de éxito", () => {
    cy.visit("/recuperar");
    cy.contains("h1", /RECUPERAR contrasena/i).should("be.visible");

    cy.fillControlledInput('form input[type="email"]', "user@test.com");
    cy.fillControlledInput('form input[type="password"]', "NuevaPass123!");
    cy.contains("form button", /actualizar contrasena/i).click();

    cy.wait("@apiRecuperar")
      .its("request.body")
      .should("deep.include", {
        correo: "user@test.com",
        nueva_contrasena: "NuevaPass123!",
      });

    cy.contains(/contrasena actualizada/i).should("be.visible");
  });
});
