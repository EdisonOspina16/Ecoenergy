describe("Regresión | Flujos críticos end-to-end", () => {
  it("flujo completo: login → home → perfil → registrar tomacorriente", () => {
    cy.loadPerfilFixtures();
    cy.loginByUi();
    cy.url().should("include", "/home");
    cy.contains(/Resumen de Consumo/i).should("be.visible");

    cy.visit("/perfil");
    cy.wait("@apiGetPerfil");
    cy.get('input[value="Lámpara Sala"]').should("exist");

    cy.get("aside").within(() => {
      cy.fillControlledInput(
        'input[placeholder*="código del dispositivo"]',
        "REG-001",
      );
      cy.fillControlledInput(
        'input[placeholder*="Cargador del móvil"]',
        "Nuevo Enchufe",
      );
    });
    cy.contains("button", /Registrar Tomacorriente/i).click();
    cy.wait("@apiPostPerfil");
    cy.contains(/Dispositivo registrado exitosamente/i).should("be.visible");
  });

  it("flujo: landing suscripción → login", () => {
    cy.mockApi({ authenticated: false });
    cy.visit("/");
    cy.fillControlledInput(
      '#comunidad input[placeholder="Tu correo electrónico"]',
      "regression@test.com",
    );
    cy.contains("button", /unirse a la comunidad/i).click();
    cy.wait("@apiSubscribe");

    cy.mockApi({ authenticated: true });
    cy.loginByUi();
    cy.url().should("include", "/home");
  });

  it("flujo: recuperar contraseña muestra éxito", () => {
    cy.mockApi({ authenticated: false });
    cy.visit("/recuperar");
    cy.fillControlledInput('form input[type="email"]', "reg@test.com");
    cy.fillControlledInput('form input[type="password"]', "NuevaClave1!");
    cy.contains("form button", /actualizar contrasena/i).click();
    cy.wait("@apiRecuperar");
    cy.contains(/contrasena actualizada/i).should("be.visible");
  });
});
