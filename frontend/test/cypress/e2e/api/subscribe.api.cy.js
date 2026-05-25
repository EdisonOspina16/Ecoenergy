describe("API | Suscripción", () => {
  beforeEach(() => {
    cy.mockApi({ authenticated: false });
  });

  it("POST /subscribe envía el email correcto", () => {
    cy.visit("/");
    cy.fillControlledInput(
      '#comunidad input[placeholder="Tu correo electrónico"]',
      "api-sub@test.com",
    );
    cy.contains("button", /unirse a la comunidad/i).click({ force: true });

    cy.wait("@apiSubscribe").then((interception) => {
      expect(interception.request.method).to.eq("POST");
      expect(interception.request.body).to.deep.equal({
        email: "api-sub@test.com",
      });
      expect(interception.response.statusCode).to.eq(200);
    });
  });
});
