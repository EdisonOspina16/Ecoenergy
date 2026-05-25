describe("API | Perfil y dispositivos", () => {
  beforeEach(() => {
    cy.loadPerfilFixtures();
    cy.loginByUi();
  });

  it("GET /perfil devuelve hogar y dispositivos", () => {
    cy.visit("/perfil");
    cy.wait("@apiGetPerfil").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
      expect(interception.response.body.success).to.eq(true);
      expect(interception.response.body.dispositivos).to.have.length(2);
    });
  });

  it("POST /perfil guarda perfil de hogar", () => {
    cy.mockApi({ authenticated: true, hogar: null, dispositivosPerfil: [] });
    cy.visit("/perfil");
    cy.wait("@apiGetPerfil");

    cy.fillControlledInput('input[placeholder="Ej: Mi Casa"]', "Hogar API");
    cy.fillControlledInput('input[placeholder*="Calle 50"]', "Dirección API");
    cy.contains("button", /guardar cambios/i).click({ force: true });

    cy.wait("@apiPostPerfil").then((interception) => {
      expect(interception.request.body).to.deep.include({
        nombre_hogar: "Hogar API",
        address: "Dirección API",
      });
      expect(interception.response.statusCode).to.eq(200);
    });
  });

  it("DELETE /perfil/dispositivo elimina tomacorriente", () => {
    cy.visit("/perfil");
    cy.wait("@apiGetPerfil");
    cy.get('button[title="Eliminar dispositivo"]').first().click({ force: true });
    cy.wait("@apiDeleteDispositivo").its("response.statusCode").should("eq", 200);
  });
});
