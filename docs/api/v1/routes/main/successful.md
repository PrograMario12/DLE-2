# 🧩 Módulo: `app/api/v1/routes/main/successful.py`

## 🔍 Visión General y Propósito del Módulo

### ⚡ TL;DR Técnico

El módulo **define y registra el endpoint `/successful`** dentro del blueprint principal de la aplicación Flask. Su objetivo es **mostrar la vista de éxito** (`successful.html`) tras una acción completada (entrada o asignación de un empleado), combinando datos de usuario (`UserService`) y del estado de estación (`StationService`).

También **valida cookies**, **maneja errores** de validación o conexión de servicios, y **unifica el contexto** para renderizar la plantilla de éxito.

---

### 🧱 Contexto Arquitectónico

* **Capa**: Presentación / Web Routing.
* **Rol dentro del sistema**: Este módulo actúa como **controlador de vista** dentro del blueprint `main`. Se comunica con servicios de dominio (`UserService`, `StationService`) para obtener datos de negocio y preparar el contexto para la capa de presentación (plantilla Jinja2).
* **Dependencias directas**:

  * `Flask` (routing, cookies, plantillas).
  * `UserService` (dominio).
  * `StationService` (dominio).
  * `EmployeeCookie` (schema Pydantic para validación).

---

### 🧩 Justificación de Diseño

* **Patrón empleado**: *Service-Oriented Controller*.

  * El módulo **no contiene lógica de negocio**; delega en servicios (`UserService`, `StationService`).
* **Validación declarativa**: Se usa `EmployeeCookie.model_validate` (Pydantic) para validar el identificador del empleado.
* **Separación de responsabilidades**: El controlador se limita a:

  1. Validar input.
  2. Invocar servicios de dominio.
  3. Componer un contexto de vista.
  4. Renderizar plantilla o redirigir según el flujo.
* **Manejo robusto de errores**: Cada interacción con un servicio está envuelta en `try/except` para aislar fallos sin afectar la UX.
* **Compatibilidad de plantilla**: El contexto mantiene nombres redundantes (e.g., `"user"` y `"line"`) para asegurar compatibilidad con HTML heredado.

---

## 📘 Referencia de API y Uso

### 🧭 Invocación / Importación

```python
from flask import Blueprint
from app.api.v1.routes.main.successful import register_successful
from app.domain.services.user_service import UserService
from app.domain.services.station_service import StationService

bp = Blueprint("main", __name__)

user_service = UserService()
station_service = StationService()

register_successful(bp, user_service, station_service)
```

---

### 🧮 Funciones Públicas

#### `register_successful(bp: Blueprint, user_service: UserService, station_service: StationService) -> None`

**Descripción**
Registra la ruta `/successful` en el blueprint especificado.
Define el controlador interno `successful()` que maneja solicitudes GET y POST.

**Flujo general:**

1. Valida cookie `employee_number`.
2. Si existe `?id=...`, registra la asignación o entrada del empleado.
3. Obtiene información del usuario y del estado de su estación.
4. Combina ambos en un contexto para renderizar `successful.html`.

**Errores manejados:**

* Cookie inválida → redirección a `main.home`.
* Falla en servicios → logs + redirección a `main.home` (gracia degradada).

---

### 🧩 Estructuras de Datos (pseudo-TypeScript)

#### Entrada: Cookie y parámetros de URL

```typescript
interface RequestInput {
  cookies: {
    employee_number: string; // número de empleado válido y positivo
  };
  query?: {
    id?: number; // identificador opcional de "side" para registrar asignación
  };
}
```

#### Esquema de validación (`EmployeeCookie`)

```typescript
interface EmployeeCookie {
  employee_number: number; // validado y convertido desde cookie string
}
```

#### Contexto de salida para plantilla (`ctx`)

```typescript
interface SuccessfulContext {
  css_href: string;        // ruta a estilos estáticos
  user: string | null;     // nombre del usuario
  line: string | null;     // nombre de la línea de producción
  station: string | null;  // estación asignada
  tipo: string | null;     // tipo de estado (e.g., 'active', 'break')
  color_class: string | null; // clase CSS asociada al estado
  image: string | null;    // ruta al archivo de imagen de usuario
}
```

---

### 💡 Ejemplo de Uso

```python
# Ejemplo de solicitud GET válida
GET /successful?id=7
Cookie: employee_number=10345

# Flujo interno:
# - Valida cookie (10345)
# - Llama user_service.register_entry_or_assignment(10345, 7)
# - Obtiene user_info y station_status
# - Renderiza successful.html con contexto final
```

---

## 🧠 Análisis de Componentes y Diseño Interno

### 🔗 Diagrama de Dependencias

```
+------------------------------+
| successful.py (Controller)   |
+------------------------------+
      | uses
      v
+--------------------------+
| UserService              | <---> DB/ORM (usuarios)
+--------------------------+

+--------------------------+
| StationService           | <---> Sistema Andon / Línea
+--------------------------+

+--------------------------+
| EmployeeCookie (Schema)  |
+--------------------------+
```

**Dependencias externas:**

* `Flask` (framework de routing y plantillas)
* `logging`, `traceback`, `sys` (manejo de logs y errores)

---

### 🔄 Flujo de Control Detallado

1. **Validación inicial de cookie**

   * Recupera `employee_number` desde cookies.
   * Verifica que sea numérico y positivo.
   * Si no lo es, registra error y redirige a `main.home`.

2. **Validación con Pydantic**

   * Usa `EmployeeCookie.model_validate()` para asegurar integridad tipada.
   * Captura `ValueError` en caso de formato incorrecto.

3. **Registro opcional de asignación**

   * Si `?id` está presente:

     * Llama a `user_service.register_entry_or_assignment()`.
     * Registra la acción (puede ser entrada o reasignación de puesto).

4. **Obtención de información de usuario**

   * Invoca `user_service.get_user_info_for_display()`.
   * En caso de excepción, continúa con `info = {}`.

5. **Obtención de estado de estación**

   * Llama `station_service.get_user_status_for_display()`.
   * En caso de error, `display = {}`.

6. **Resolución de imagen**

   * Prioriza `display["image"]`.
   * Si no existe, construye `<id>.png` desde `info["id"]`.

7. **Composición del contexto y renderizado**

   * Combina ambos diccionarios (`info`, `display`).
   * Renderiza `successful.html` con los valores.

---

### 🧩 Consideraciones de Patrones

* **Patrón MVC (Controller Layer)**: separa lógica de control de servicios de dominio.
* **Patrón Façade (servicios)**: `UserService` y `StationService` encapsulan la complejidad de fuentes de datos subyacentes.
* **Patrón Adapter**: El contexto generado actúa como un adaptador entre estructuras de datos internas y la plantilla HTML.

---

## 📈 Métricas Clave y Consideraciones Técnicas

### ⚠️ Limitaciones Conocidas

* No maneja expiración ni renovación de cookies (posible mejora futura).
* Errores de servicio externos se manejan con logs, pero no se notifica al usuario.
* No existen mecanismos de caching para los datos de usuario o estación.

---

### 🧩 Requisitos y Entorno

* **Python:** ≥ 3.10
* **Flask:** ≥ 2.3
* **Pydantic:** ≥ 2.0
* **Servicios dependientes:** `UserService`, `StationService` implementados y disponibles.
* **Plantilla:** `templates/successful.html` accesible.

---

### 🚀 Consideraciones de Rendimiento / Escalabilidad

* La ruta es **read-heavy**; el cuello de botella potencial es la consulta a `UserService`.
* Los servicios pueden beneficiarse de caching (por `employee_number`).
* Todas las llamadas son síncronas: para alta concurrencia, evaluar `async Flask` o un worker pool para llamadas a servicios.

---

## 🧪 Desarrollo y Mantenimiento

### 🧰 Proceso de Pruebas

* **Ubicación esperada:** `tests/api/v1/routes/main/test_successful.py`
* **Mocks requeridos:**

  * `UserService.register_entry_or_assignment`
  * `UserService.get_user_info_for_display`
  * `StationService.get_user_status_for_display`
* **Casos a cubrir:**

  1. Cookie inválida → redirección.
  2. Cookie válida + sin `id` → render de éxito.
  3. Cookie válida + con `id` → registro + render.
  4. Excepciones controladas → logs + redirección.

---

### 🧩 Guía de Contribución

Para extender el comportamiento del endpoint:

> **Ejemplo: agregar lógica para registrar salida de turno**

1. Implementa un método `UserService.register_exit(employee_number: int)`.
2. Extiende el bloque `if side_id:` para manejar una nueva query `action=exit`.
3. Añade el campo `exit_time` al contexto (`ctx`).
4. Actualiza la plantilla `successful.html` para reflejarlo.

---

### 🪲 Notas de Depuración (Debugging)

* **Punto de entrada:** función interna `successful()`.
* **Depurar cookie:** imprimir `request.cookies` antes de validación.
* **Depurar fallos de servicio:** revisar logs `app.log` con `logger.error(...)`.
* **Render Context Dump:** insertar temporalmente:

  ```python
  print(ctx)
  ```

  antes del `render_template` para inspeccionar valores renderizados.
