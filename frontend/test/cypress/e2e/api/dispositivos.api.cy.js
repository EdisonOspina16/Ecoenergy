describe("API | Dispositivos simulados", () => {
  beforeEach(() => {
    cy.loadPerfilFixtures();
    cy.loginByUi();
    cy.visit("/home");
  });

  it("GET /dispositivos retorna lista con estados", () => {
    cy.wait("@apiDispositivos").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
      expect(interception.response.body.dispositivos).to.be.an("array");
      expect(interception.response.body.dispositivos[0].estado).to.eq("Encendido");
    });
  });
});
