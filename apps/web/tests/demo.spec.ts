import { test, expect } from "@playwright/test";

test("demo: catálogo, archivo, propuesta y optimización supervisada", async ({
  page,
}, testInfo) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Explorá tu espacio" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Entrar al demo" }),
  ).toBeEnabled();
  if (testInfo.project.name === "mobile")
    await page
      .getByLabel("Empresa", { exact: true })
      .selectOption("norte-demo");
  await page.getByRole("button", { name: "Entrar al demo" }).click();
  await expect(
    page.getByRole("heading", { name: "Una mirada a tu publicidad" }),
  ).toBeVisible();
  await expect(
    page.getByText("Meta está desconectado.", { exact: false }).first(),
  ).toBeVisible();
  if (process.env.E2E_SCREENSHOT && testInfo.project.name === "desktop")
    await page.screenshot({ path: process.env.E2E_SCREENSHOT, fullPage: true });
  await page
    .getByRole("navigation")
    .getByRole("button", { name: "Productos", exact: true })
    .click();
  const name = `Producto E2E ${Date.now()}`;
  await page.getByLabel("Nombre", { exact: true }).fill(name);
  await page
    .getByLabel("Descripción")
    .fill("Producto creado por una prueba automatizada.");
  await page.getByLabel("Precio (UYU)").fill("1250");
  await page.getByRole("button", { name: "Agregar al catálogo" }).click();
  await expect(page.getByRole("heading", { name })).toBeVisible();
  await page
    .getByRole("navigation")
    .getByRole("button", { name: "Anuncios", exact: true })
    .click();
  await page
    .getByLabel("Producto", { exact: true })
    .selectOption({ label: name });
  await page
    .getByLabel("Archivo · hasta 25 MiB")
    .setInputFiles("tests/fixtures/creative.png");
  await page
    .getByLabel("Texto del anuncio")
    .fill("Conocé este producto de demostración.");
  await page.getByRole("button", { name: "Cargar y analizar" }).click();
  await expect(
    page.getByRole("heading", { name: "creative.png" }),
  ).toBeVisible();
  await page
    .getByRole("navigation")
    .getByRole("button", { name: "Planificador", exact: true })
    .click();
  await page
    .getByLabel("Producto", { exact: true })
    .selectOption({ label: name });
  await page.getByRole("checkbox", { name: "creative.png" }).check();
  await page.getByRole("button", { name: "Generar propuesta" }).click();
  await expect(
    page.getByRole("heading", { name: `${name} · ABO` }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Aprobar propuesta" }).first().click();
  await expect(
    page.getByRole("status").filter({ hasText: "No se publicó en Meta" }),
  ).toBeVisible();
  await page
    .getByRole("navigation")
    .getByRole("button", { name: /Optimización/ })
    .click();
  await page.getByRole("button", { name: "Evaluar campañas" }).click();
  await expect(
    page.getByRole("heading", { name: "Pausar campaña" }).first(),
  ).toBeVisible();
  const pause = page
    .locator("article.recommendation")
    .filter({ has: page.getByRole("heading", { name: "Pausar campaña" }) })
    .first();
  await pause.getByRole("button", { name: "Aprobar cambio" }).click();
  await pause.getByRole("button", { name: "Aplicar simulación" }).click();
  await expect(
    page.getByRole("status").filter({ hasText: "No hubo cambios en Meta" }),
  ).toBeVisible();
  await page
    .getByRole("navigation")
    .getByRole("button", { name: "Resumen", exact: true })
    .click();
  await expect(page.getByText("Pausada · demo", { exact: true })).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Una mirada a tu publicidad" }),
  ).toBeVisible();
});

test("rol lector y segundo espacio de trabajo", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Entrar al demo" }),
  ).toBeEnabled();
  await page.getByLabel("Empresa", { exact: true }).selectOption("norte-demo");
  await page.getByLabel("Acceso de prueba").selectOption("viewer");
  await page.getByRole("button", { name: "Entrar al demo" }).click();
  await expect(
    page.getByRole("heading", { name: "Una mirada a tu publicidad" }),
  ).toBeVisible();
  await page
    .getByRole("navigation")
    .getByRole("button", { name: "Productos", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Botella térmica" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Agregar al catálogo" }),
  ).toHaveCount(0);
  await page
    .getByRole("navigation")
    .getByRole("button", { name: /Optimización/ })
    .click();
  await expect(
    page.getByRole("button", { name: "Evaluar campañas" }),
  ).toBeDisabled();
});
