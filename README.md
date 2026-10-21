# API de Automóviles

API de solo lectura para consultar automóviles en Amazon RDS MySQL mediante un procedimiento almacenado. Está pensada para Windows local y Windows Server 2025 en EC2. No contiene datos de demostración ni operaciones para crear, modificar o borrar registros.

## Requisitos

- Python 3.10 o posterior (64 bits recomendado).
- Acceso de red a RDS para los endpoints de base de datos. La aplicación y `/health` arrancan aunque RDS todavía no esté disponible.
- El estudiante 1 debe proporcionar los datos de conexión y el contrato real del procedimiento (detalles al final).

## Windows: instalación y ejecución

En PowerShell, desde la carpeta del proyecto:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Completa el `.env` con los valores reales recibidos. No guardes ese archivo en GitHub. Para desarrollo local:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000
```

La API queda en `http://localhost:5000`, Swagger en `http://localhost:5000/docs` y OpenAPI en `/openapi.json`. `0.0.0.0` permite escuchar en interfaces de red; para acceso remoto también se requieren reglas de red y firewall apropiadas. El endpoint `/health` no consulta RDS.

Para las pruebas automatizadas:

```powershell
pytest -q
```

Las pruebas usan mocks y no sustituyen la operación normal de la API por registros ficticios. Sin RDS configurado, los endpoints dependientes devuelven un error claro.

## Endpoints

- `GET /health`: estado del proceso, sin dependencia de RDS.
- `GET /health/db`: abre una conexión y ejecuta `SELECT 1`.
- `GET /api/automoviles`: llama al procedimiento indicado por `DB_PROCEDURE_AUTOMOVILES` y serializa las columnas recibidas en JSON.
- `GET /docs`: Swagger UI.

Errores de configuración o conexión devuelven HTTP 503; procedimiento no encontrado devuelve 502; otros errores SQL devuelven 500. Las respuestas y logs no incluyen contraseña. La llamada se hace con `cursor.callproc` y el nombre se valida como identificador simple o `esquema.nombre`, sin datos SQL del usuario.

## Procedimiento y contrato de datos

No se presupone nombre, tablas ni columnas. El estudiante 1 debe confirmar el nombre exacto y cómo invocarlo, si requiere parámetros (esta versión contempla un procedimiento sin parámetros), y el result set que entrega. El procedimiento debe retornar un conjunto de resultados con nombres de columna; esos nombres se convierten dinámicamente en claves JSON. Si requiere parámetros o devuelve múltiples conjuntos con semántica distinta, acuerden el contrato antes de adaptar `app/db.py`.

## GitHub

Verifica que `.env` no esté versionado; `.gitignore` lo excluye. Publica únicamente placeholders en `.env.example`:

```powershell
git init
git add .
git status
git commit -m "Crear API de consulta de automoviles"
git branch -M main
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```

Reemplaza la URL por el repositorio creado. Si `.env` aparece en `git status`, detente y corrige el staging antes del commit. Las credenciales se configuran por separado en el `.env` de cada entorno.

## Despliegue en EC2 Windows Server 2025

1. Clona el repositorio, instala Python y sigue los pasos de instalación anteriores.
2. Crea `.env` en la carpeta clonada (no lo descargues de GitHub) con los valores aprobados por el propietario de RDS.
3. Ejecuta `python -m uvicorn app.main:app --host 0.0.0.0 --port 5000`. Para ejecución persistente, configura un servicio Windows con un administrador autorizado; esta guía no crea servicios ni modifica AWS.
4. Comprueba localmente en EC2 `http://127.0.0.1:5000/health`, luego `/health/db` y `/api/automoviles`.

## Red y seguridad AWS

- **TCP 5000:** permite entrada al Security Group de EC2 solo desde los clientes/orígenes autorizados o desde el proxy de Vercel según la arquitectura aprobada. Limita también Windows Defender Firewall al origen necesario. No abras `0.0.0.0/0` indiscriminadamente.
- **TCP 3306:** permite entrada al Security Group de RDS únicamente desde el Security Group de EC2, si ambos están en una VPC que permite esa referencia, o desde el CIDR/origen privado autorizado. No expongas MySQL públicamente.
- **Security Groups** son firewalls con estado que permiten tráfico; por sí solos no crean conectividad entre redes. **Tablas de rutas** deben incluir rutas en ambos sentidos. Para VPC distintas, configura **VPC Peering** (o la conectividad privada aprobada), rutas en ambas VPC y reglas de Security Group compatibles; revisa solapamiento de CIDR y DNS según se necesite.
- **ICMP/ping** es independiente de TCP. Un ping fallido no demuestra que TCP 3306 o 5000 falle; diagnostica los puertos directamente.
- CORS se configura con orígenes explícitos en `CORS_ORIGINS`. En producción se prevé que el frontend Vercel consuma `/api/automoviles` a través de su proxy inverso; configura ahí la ruta pública y evita exponer credenciales de RDS al navegador. Añade el dominio de desarrollo/cliente a CORS solo si la conexión directa está autorizada.

## Diagnóstico

Desde el equipo local:

```powershell
Invoke-RestMethod http://localhost:5000/health
Test-NetConnection ENDPOINT_RDS -Port 3306
```

Desde EC2:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health
Invoke-RestMethod http://127.0.0.1:5000/health/db
Test-NetConnection ENDPOINT_RDS -Port 3306
```

Desde un cliente autorizado del examen (sustituye la IP/DNS pública o privada aprobada):

```powershell
Test-NetConnection HOST_EC2 -Port 5000
Invoke-RestMethod http://HOST_EC2:5000/health
Invoke-RestMethod http://HOST_EC2:5000/api/automoviles
```

Si las APIs están detrás del proxy Vercel, prueba la URL pública configurada para `/api/automoviles`. El origen Vercel debe poder alcanzar EC2 por la red definida; el navegador no debe conectarse a RDS.

## Valores que solicitar al estudiante 1

1. Endpoint DNS de RDS y puerto (normalmente 3306), nombre de base de datos, usuario de solo lectura y contraseña por un canal seguro.
2. Nombre exacto del procedimiento almacenado, esquema si aplica, confirmación de que no requiere parámetros y permisos `EXECUTE` para el usuario.
3. Contrato del resultado: columnas/tipos, formato esperado y confirmación de que retorna un result set compatible.
4. Región/VPC/subredes, CIDR o Security Group de origen que debe autorizarse y si hay peering/conectividad privada entre las cuentas/VPC.

Configura esos datos únicamente en el `.env` local y en el `.env` de EC2. No los incluyas en GitHub, capturas ni respuestas de soporte.
