# Despliegue a AWS ECS con GitHub Actions

Este documento describe cómo configurar y ejecutar el pipeline de despliegue a AWS ECS definido en `.github/workflows/deploy-aws-ecs.yml`.

## Descripción general

El workflow realiza:

1. **Build y push de imagen Docker** a Amazon ECR con:
   - Tag basado en el SHA corto del commit (ej. `abc1234`).
   - Tag `latest` adicional cuando el push es a la rama `main`.
2. **Despliegue a ECS**:
   - Obtiene la Task Definition actual del servicio ECS.
   - Parchea la definición de tarea para usar la nueva imagen.
   - Registra una nueva revisión de la Task Definition.
   - Actualiza el servicio ECS y espera a que estabilice.

---

## Cuándo se ejecuta

| Evento | Comportamiento |
|--------|---------------|
| `push` a `main` | Ejecuta build + deploy automáticamente |
| `push` de un tag `v*` | Ejecuta build + deploy automáticamente |
| `workflow_dispatch` | Ejecución manual desde la UI de GitHub Actions |

---

## Requisitos previos en AWS

### 1. Configurar OIDC (autenticación sin credenciales de larga duración)

El workflow usa **OIDC** para autenticarse en AWS sin almacenar Access Keys. Necesitas:

1. Crear un **Identity Provider OIDC** en tu cuenta AWS:
   - URL del proveedor: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`

2. Crear un **IAM Role** que confíe en ese proveedor con la condición:
   ```json
   {
     "StringLike": {
       "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/YOUR_REPO:*"
     }
   }
   ```

3. Adjuntar al rol las políticas necesarias:
   - `AmazonEC2ContainerRegistryPowerUser` (push a ECR)
   - Permisos ECS: `ecs:DescribeServices`, `ecs:DescribeTaskDefinition`, `ecs:RegisterTaskDefinition`, `ecs:UpdateService`, `ecs:DescribeTaskSets`

---

## Secrets y Variables requeridos en GitHub

Ve a **Settings → Secrets and variables → Actions** en tu repositorio y agrega:

### Secrets (`New repository secret`)

| Nombre | Descripción | Ejemplo |
|--------|-------------|---------|
| `AWS_ROLE_ARN` | ARN del IAM Role a asumir vía OIDC | `arn:aws:iam::123456789012:role/GitHubActionsDeployRole` |

### Variables (`New repository variable`)

| Nombre | Descripción | Ejemplo |
|--------|-------------|---------|
| `AWS_REGION` | Región de AWS donde están los recursos | `us-east-1` |
| `ECR_REPOSITORY_URL` | URL completa del repositorio ECR | `123456789012.dkr.ecr.us-east-1.amazonaws.com/your-repo-name` |
| `ECS_CLUSTER_NAME` | Nombre del cluster ECS | `practicas-itm` |
| `ECS_SERVICE_NAME` | Nombre del servicio ECS | `practicas-itm-service` |
| `ECS_CONTAINER_NAME` | Nombre del contenedor dentro de la Task Definition | `practicas-itm` |

> **Nota**: `AWS_ROLE_ARN` se guarda como **secret** porque puede contener información sensible del ARN. Las demás pueden guardarse como **variables** (no son confidenciales).

---

## Ejecución manual (`workflow_dispatch`)

Para disparar el despliegue manualmente:

1. Ve a **Actions** en tu repositorio.
2. En el panel izquierdo selecciona **"Deploy to AWS ECS"**.
3. Haz clic en **"Run workflow"**.
4. Selecciona la rama o tag que deseas desplegar.
5. Haz clic en **"Run workflow"** (botón verde).

---

## Alternativa: Access Keys (sin OIDC)

Si no puedes configurar OIDC, puedes usar credenciales de usuario IAM:

1. Reemplaza el step `Configure AWS credentials (OIDC)` por:
   ```yaml
   - name: Configure AWS credentials (Access Keys)
     uses: aws-actions/configure-aws-credentials@v4
     with:
       aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
       aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
       aws-region: ${{ vars.AWS_REGION }}
   ```
2. Elimina el bloque `permissions: id-token: write`.
3. Agrega los secrets `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`.

> **No se recomienda** esta opción en producción. OIDC es más seguro porque no guarda credenciales de larga duración.

---

## Verificación del despliegue

Una vez ejecutado el workflow:

1. En **GitHub Actions**, cada step muestra logs detallados.
2. En la **consola de AWS → ECS → Clusters → practicas-itm → Services**, puedes ver la nueva Task Definition activa y el estado `STEADY_STATE`.
3. El step `Wait for ECS service to stabilise` falla si el servicio no estabiliza en el tiempo máximo (10 min por defecto de AWS CLI).
