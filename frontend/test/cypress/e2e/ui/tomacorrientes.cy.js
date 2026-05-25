describe("UI | Tomacorrientes", () => {
  beforeEach(() => {
    cy.loadPerfilFixtures();
    cy.loginByUi();
    cy.visit("/perfil");
    cy.wait("@apiGetPerfil");
  });

  it("lista tomacorrientes registrados", () => {
    cy.contains("h2", /Mis Dispositivos/i).should("be.visible");
    cy.get('input[value="Lámpara Sala"]').should("exist");
    cy.get('input[value="Televisor"]').should("exist");
    cy.contains("Conectado").should("be.visible");
    cy.contains("Desconectado").should("be.visible");
  });

  it("registra un nuevo tomacorriente", () => {
    cy.get("aside").within(() => {
      cy.fillControlledInput(
        'input[placeholder*="código del dispositivo"]',
        "IOT-CYP-001",
      );
      cy.fillControlledInput(
        'input[placeholder*="Cargador del móvil"]',
        "Enchufe Cocina",
      );
    });

    cy.contains("button", /Registrar Tomacorriente/i).click({ force: true });

    cy.wait("@apiPostPerfil")
      .its("request.body")
      .should("deep.include", {
        deviceId: "IOT-CYP-001",
        nickname: "Enchufe Cocina",
      });

    cy.contains(/registrado exitosamente/i).should("be.visible");
  });

  it("elimina un tomacorriente", () => {
    cy.get('button[title="Eliminar dispositivo"]').first().click({ force: true });
    cy.wait("@apiDeleteDispositivo");
    cy.contains(/eliminado exitosamente/i).should("be.visible");
  });
});
