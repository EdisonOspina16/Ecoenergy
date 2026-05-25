const { defineConfig } = require("cypress");

module.exports = defineConfig({
  projectId: "jbutds",
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL || "http://localhost:3000",
    specPattern: "e2e/**/*.cy.js",
    supportFile: "support/e2e.js",
    fixturesFolder: "fixtures",
    defaultCommandTimeout: 12000,
    requestTimeout: 15000,
    video: false,
    screenshotOnRunFailure: true,
    env: {
      apiUrl: process.env.CYPRESS_API_URL || "http://localhost:5000",
      testEmail: "cypress@test.ecoenergy",
      testPassword: "CypressTest123!",
    },
  },
});
