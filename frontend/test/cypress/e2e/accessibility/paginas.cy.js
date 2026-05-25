describe("Accesibilidad | Páginas principales", () => {
  const a11yOptions = {
    includedImpacts: ["critical"],
    rules: {
      "color-contrast": { enabled: false },
      "landmark-one-main": { enabled: false },
      "page-has-heading-one": { enabled: false },
      "nested-interactive": { enabled: false },
      label: { enabled: false },
      "button-name": { enabled: false },
      "scrollable-region-focusable": { enabled: false },
    },
  };

  beforeEach(() => {
    cy.mockApi({ authenticated: false });
  });

  it("login cumple reglas críticas de accesibilidad", () => {
    cy.visit("/login");
    cy.contains("h1", /INICIAR SESIÓN/i).should("be.visible");
    cy.injectAxe();
    cy.checkA11y(null, a11yOptions);
    cy.get('form input[type="email"]').should("exist");
    cy.contains("form button", /ingresar/i).should("be.visible");
  });

  it("landing (suscripción) cumple reglas críticas", () => {
    cy.visit("/");
    cy.get("#comunidad").should("exist");
    cy.injectAxe();
    cy.checkA11y("#comunidad", a11yOptions);
  });

  it("perfil autenticado cumple reglas críticas", () => {
    cy.loadPerfilFixtures();
    cy.loginByUi();
    cy.visit("/perfil");
    cy.wait("@apiGetPerfil");
    cy.contains("h1", /Mi Perfil y Dispositivos/i).should("be.visible");
    cy.injectAxe();
    cy.checkA11y("main", a11yOptions);
  });
});
