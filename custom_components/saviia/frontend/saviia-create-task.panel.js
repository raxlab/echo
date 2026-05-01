import { LitElement, html } from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";
import { Styles } from "./styles/index.js";
import { createLogger } from "./services/logger.js";
import TasksAPI from './endpoints/tasks.endpoints.js';

const logger = createLogger("SaviiaCreateTask");
logger.info("SAVIIA Create Tasks panel loading...");

export class SaviiaCreateTask extends LitElement {
  set hass(hass) {
    this._hass = hass;

    if (!this.tasksAPI || this.tasksAPI.hass !== hass) {
      this.tasksAPI = new TasksAPI(hass);
    }

    if (!this._initialized && hass) {
      this._initialized = true;
      // Fetch people stored in HA via websocket
      this._fetchPeople();
    }
  }
  static properties = {
    hass: { type: Object },
    images: { state: true },
    isSubmitting: { state: true },
    people: { state: true }
  };

  constructor() {
    super();
    this.images = [];
    this.tasksAPI = new TasksAPI();
    this.isSubmitting = false;
    this.people = [];
    this.CONFIG = {
      ACCEPTED_IMAGE_TYPES: ["image/jpeg", "image/png", "image/gif"],
    };
  }

  async _fetchPeople() {
    try {
      const people = await this.tasksAPI.getPeople();
      console.log("Fetched people:", people);
      if (Array.isArray(people)) this.people = people;
    } catch (err) {
      logger.error("Error fetching people via TasksAPI:", err);
      this.people = [];
    }
  }

  _onPersonSelected(e) {
    const idx = e.target.value;
    if (!idx) return;
    const person = this.people.find((p) => p.id == idx) || this.people[idx];
    if (!person) return;
    // Populate form fields
    const form = this.renderRoot?.querySelector?.("form") || document;
    const assigneeInput = form.querySelector("#assignee");
    const emailInput = form.querySelector("#assignee_email");
    const discordInput = form.querySelector("#assignee_discord_username");
    if (assigneeInput) assigneeInput.value = person.name || "";
    if (emailInput) emailInput.value = person.email || "";
    if (discordInput) discordInput.value = person.discord || "";
  }

  static styles = new Styles().getStyles(['general', 'form', 'alert'])

  getPeriodicity(periodicity, num) {
    if (!periodicity) return "Sin periodicidad";

    const map = {
      daily: "día(s)",
      weekly: "semana(s)",
      monthly: "mes(es)",
      yearly: "año(s)",
    };

    return `Cada ${num} ${map[periodicity] ?? ""}`;
  }

  handleFiles(files) {
    [...files].forEach((file) => {
      if (!this.CONFIG.ACCEPTED_IMAGE_TYPES.includes(file.type)) return;

      const reader = new FileReader();

      reader.onload = () => {
        const img = {
          name: file.name,
          type: file.type,
          data: reader.result.split(",")[1],
        };

        this.images = [...this.images, img];
      };

      reader.readAsDataURL(file);
    });
  }

  deleteImage(index) {
    this.images = this.images.filter((_, i) => i !== index);
  }

  onDrop(e) {
    e.preventDefault();
    if (e.dataTransfer?.files) this.handleFiles(e.dataTransfer.files);
  }

  onFileInput(e) {
    const input = e.target;
    if (input.files) this.handleFiles(input.files);
  }

  async submitTask(e) {
    e.preventDefault();
    this.isSubmitting = true;
    let cantSubmit = false;

    const form = e.target;

    const title = form.querySelector("#task-title").value;
    const deadline = form.querySelector("#deadline").value;
    const priorityNum = parseInt(form.querySelector("#priority").value);
    const assignee = form.querySelector("#assignee").value;
    let periodicity = form.querySelector("#periodicity").value || "Sin periodicidad";
    const periodicityNum = form.querySelector("#periodicity-number").value;
    const description = form.querySelector("#details").value || "Sin descripción";
    const category = form.querySelector("#categ").value || "Sin categoría";
    const creation = form.querySelector("#creation").value;
    const execution = form.querySelector("#execution").value;
    const assignee_email = form.querySelector("#assignee_email").value || "";
    const assignee_discord_username = form.querySelector("#assignee_discord_username").value || "";

    const task = {
      title: title,
      description: description,
      deadline: deadline,
      priority: priorityNum,
      assignee: assignee,
      category: category,
      periodicity: periodicity !== "Sin periodicidad"
        ? this.getPeriodicity(periodicity, periodicityNum)
        : periodicity,
      creation: creation,
      execution: execution,
      assignee_email: assignee_email,
      assignee_discord_username: assignee_discord_username
    }
    // Parameters validation
    if (periodicity !== "Sin periodicidad" && !periodicityNum) {
      alert("Por favor, indica el número de periodicidad para la repetición de esta tarea.");
      this.isSubmitting = false;
      return;
    }
    if (this.images.length > 10) {
      alert("No puedes agregar más de 10 imágenes a una tarea.");
      this.isSubmitting = false;
      return;
    }


    try {
      const response = await this.tasksAPI.createTask(task, this.images)
      logger.debug("Response:", response);
    } catch (err) {
      logger.error(err);
      alert(`Hubo un error al crear la tarea. Por favor, inténtalo de nuevo ${err.message}`);
      cantSubmit = true;
    } finally {
      if (!cantSubmit) {
        alert("Tarea creada con éxito ✅");
      }
      this.isSubmitting = false;
      this.images = [];
      form.reset();
    }
  }

  render() {
    return html`
    <h2>Crea una nueva tarea</h2>
    <p>Completa el siguiente formulario para generar una nueva tarea</p>
    <p><i>Los campos marcados con <span style="color: #03a9f4">*</span> son obligatorios.</i></p>

    <form @submit=${this.submitTask}>
    <fieldset>
      <legend>Detalles generales de la tarea</legend>

      <label>
        <p>Nombre de la tarea <span style="color: #03a9f4">*</span> </p>
        <input id="task-title" required placeholder="Nombre" />
      </label>
      
      <label>
        <p>Fecha de creación de la tarea <span style="color: #03a9f4">*</span> </p>
        <i>Fecha en la que el autor registró la tarea en el formulario.</i>
        <input id="creation" type="date" required/>
      </label>

      <label>
        <p>Fecha limite de la tarea <span style="color: #03a9f4">*</span> </p>
        <i>La(s) persona(s) asignadas a esta tarea deben finalizarla antes de la fecha determinada.</i>
        <input id="deadline" type="date" required />
      </label>
      
      <label>
        <p>Fecha de realización de la tarea </p>
        <i>Fecha cuando el usuario logró completar la tarea.</i>
        <input id="execution" type="date"/>
      </label>
      
      <label>
        <p>Prioridad <span style="color: #03a9f4">*</span> </p>
          <i>1 es la prioridad más alta y 4 la más baja</i>
        <input id="priority" type="range" min="1" max="4" />
        <ul id="priority-nums">
          <li>1</li>
          <li>2</li>
          <li>3</li>
          <li>4</li>
        </ul>
      </label>
    </fieldset>

    <fieldset>
      <legend>Detalles del responsable de la tarea</legend>
      <label>
        <p>Seleccionar persona</p>
        <i>Elige una persona almacenada en Saviia (autocompleta el formulario).</i>
        <select id="people-select" @change=${this._onPersonSelected}>
          <option value="">-- Manual --</option>
          ${this.people.map(
            (p) => html`<option value="${p.id}">${p.name} ${p.email ? `(${p.email})` : ""}</option>`
          )}
        </select>
      </label>
      <label>
        <p>Persona asignada <span style="color: #03a9f4">*</span> </p>
        <i>La persona responsable de realizar esta tarea.</i>
        <input id="assignee" type="text" required />
      </label>

      <label>
        <p>Email</span> </p>
        <i>Correo electrónico de la persona responsable</i>
        <input id="assignee_email" type="email" />
      </label>
      
      <label>
        <p>Nombre de usuario en Discord</span> </p>
        <i>Nombre de usuario en Discord del responsable. Formato: @username.</i>
        <input id="assignee_discord_username" type="text" placeholder="@username" />
      </label>
    </fieldset>

    <fieldset>
    <legend>Detalles adicionales de la tarea</legend>
      <label>
        <p>Periodicidad</p>
        <i>Indica si esta tarea se repite en un intervalo de tiempo específico.</i>
        <select id="periodicity">
          <option value="Sin periodicidad" selected>Ninguna</option>
          <option value="daily">Diaria</option>
          <option value="weekly">Semanal</option>
          <option value="monthly">Mensual</option>
          <option value="yearly">Anual</option>
        </select>
        <br><br><i>Indica cuántas veces se repite esta tarea en el intervalo seleccionado. Por ejemplo, si el
          usuario define una repetición diaria, entonces se repetirá cada cierto número de días.</i>
        <input id="periodicity-number" type="number" min="1" placeholder="Número de periodicidad" />
      </label>
      <label>
        <p>Categoría</p>
        <i>La categoría a la que pertenece esta tarea (opcional).</i>
        <input id="categ" type="text" />
        </label>
        <label>
        <p>Detalle de la tarea</p>
        <i>Describe los detalles específicos de la tarea, ya sea para aclarar o para dar instrucciones.</i>
        <textarea id="details" rows="4"></textarea>
      </label>
    </fieldset>
    
    <fieldset>
      <legend>Imágenes</legend>
      <i>Arrastra imágenes aquí o haz click para seleccionarlas. Solo se pueden agregar hasta un máximo de 10 imágenes.</i>
      <div
      id="dropzone"
      @drop=${this.onDrop}
      @dragover=${(e) => e.preventDefault()}
      >
      <input
      id="file-input"
      type="file"
      accept="image/*"
      multiple
      @change=${this.onFileInput}
      >
      <label for="file-input" id="file-input-label">Haz click para agregar tus imagenes o arrastralas</label>
      </div>
      <div id="preview">
      ${this.images.map((img, i) => html`
        <div class="preview-img-wrapper">
        <img src="data:${img.type};base64,${img.data}" />
        <button
          type="button"
          class="delete-img-btn"
          @click=${() => this.deleteImage(i)}
        >
          X
        </button>
        </div>
      `)}
      </div>
    </fieldset>

    <button ?disabled=${this.isSubmitting}>
      ${this.isSubmitting ? "Enviando..." : "Enviar tarea"}
    </button>
    </form>
  `;
  }
}

customElements.define("saviia-create-task", SaviiaCreateTask);
