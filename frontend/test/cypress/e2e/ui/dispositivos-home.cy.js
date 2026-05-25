describe("UI | Listar dispositivos y estado en home", () => {
  beforeEach(() => {
    cy.loadPerfilFixtures();
    cy.loginByUi();
    cy.visit("/home");
    cy.wait("@apiGetPerfil");
    cy.wait("@apiDispositivos");
  });

  it("lista dispositivos conectados con su estado", () => {
    cy.contains("h2", /Consumo por Dispositivo/i).should("be.visible");
    cy.contains("Lámpara Sala").should("be.visible");
    cy.contains("Televisor").should("be.visible");
    cy.contains("Encendido").should("be.visible");
    cy.contains("Apagado").should("be.visible");
  });
});
