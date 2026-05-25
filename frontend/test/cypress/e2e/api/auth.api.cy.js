describe("API | Autenticación", () => {
  it("POST /login desde UI responde 200 con redirect /home", () => {
    cy.mockApi({ authenticated: true });
    cy.loginByUi();
    cy.get("@apiLogin").its("response.statusCode").should("eq", 200);
    cy.get("@apiLogin").its("response.body.redirect").should("eq", "/home");
  });

  it("intercepta login desde la UI y valida el payload", () => {
    cy.mockApi({ authenticated: true });
    cy.loginByUi("api@test.com", "Secret123!");
    cy.get("@apiLogin")
      .its("request.body")
      .should("deep.equal", { correo: "api@test.com", contrasena: "Secret123!" });
  });
});
