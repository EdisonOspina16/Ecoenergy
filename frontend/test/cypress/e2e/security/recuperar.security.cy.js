describe("Seguridad | Cambiar contraseña", () => {
  beforeEach(() => {
    cy.mockApi({ authenticated: false });
  });

  it("envía credenciales por POST /recuperar sin exponerlas en la URL", () => {
    cy.visit("/recuperar");
    cy.fillControlledInput('form input[type="email"]', "seguro@test.com");
    cy.fillControlledInput('form input[type="password"]', "ClaveSegura99!");
    cy.contains("form button", /actualizar contrasena/i).click();

    cy.wait("@apiRecuperar").then((interception) => {
      expect(interception.request.method).to.eq("POST");
      expect(interception.request.body.nueva_contrasena).to.eq("ClaveSegura99!");
      expect(interception.request.url).not.to.include("ClaveSegura99!");
    });
    cy.url().should("include", "/recuperar");
  });
});
