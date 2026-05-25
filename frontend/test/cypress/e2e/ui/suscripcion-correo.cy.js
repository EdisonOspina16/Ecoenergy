describe("UI | Suscripción correo", () => {
  beforeEach(() => {
    cy.mockApi({ authenticated: false });
  });

  it("suscribe un correo desde la landing", () => {
    cy.visit("/");
    cy.get("#comunidad").scrollIntoView();
    cy.fillControlledInput(
      '#comunidad input[placeholder="Tu correo electrónico"]',
      "nuevo@suscriptor.com",
    );
    cy.contains("button", /unirse a la comunidad/i).click({ force: true });

    cy.wait("@apiSubscribe")
      .its("request.body")
      .should("deep.equal", { email: "nuevo@suscriptor.com" });

    cy.contains(/gracias por unirte/i).should("be.visible");
  });
});
