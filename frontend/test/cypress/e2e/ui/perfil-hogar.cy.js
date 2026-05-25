describe("UI | Crear perfil hogar", () => {
  beforeEach(() => {
    cy.mockApi({ authenticated: true, hogar: null, dispositivosPerfil: [] });
    cy.loginByUi();
    cy.visit("/perfil");
    cy.wait("@apiGetPerfil");
  });

  it("guarda el perfil del hogar con datos válidos", () => {
    cy.contains("h2", /Perfil del Hogar/i).should("be.visible");
    cy.fillControlledInput('input[placeholder="Ej: Mi Casa"]', "Mi Casa Cypress");
    cy.fillControlledInput(
      'input[placeholder*="Calle 50"]',
      "Calle 50 #45-32, Medellín, Antioquia",
    );

    cy.contains("button", /guardar cambios/i).click({ force: true });
    cy.wait("@apiPostPerfil").its("request.body").should("deep.include", {
      nombre_hogar: "Mi Casa Cypress",
      address: "Calle 50 #45-32, Medellín, Antioquia",
    });

    cy.contains(/perfil creado exitosamente/i).should("be.visible");
  });
});
