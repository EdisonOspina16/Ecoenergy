require("cypress-axe");
require("./apiMocks");

// Next.js en dev puede lanzar hydration mismatch (Font Awesome en layout); no fallar E2E por eso.
Cypress.on("uncaught:exception", (err) => {
  if (err.message && err.message.includes("Hydration failed")) {
    return false;
  }
  return undefined;
});

beforeEach(() => {
  cy.on("window:confirm", (text) => {
    expect(text).to.match(/eliminar este dispositivo/i);
    return true;
  });
});
