import { createLogger } from "../services/logger.js";

const logger = createLogger("TasksAPI");


export default class TasksAPI {
    constructor(hass = null) {
        this.hass = hass;
        this.environment = this._detectEnvironment();
        if (this.environment === "development") {
            this.baseUrl = import.meta.env?.VITE_HA_URL;
            this.token = import.meta.env?.VITE_HA_TOKEN;
            this._hassHeaders = {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        }
        logger.info("Initialized", { environment: this.environment });
    }

    _detectEnvironment() {
        try {
            const location = window.location;
            if (location.hostname === "localhost" && location.port === "8000") {
                return "development";
            }
        } catch (error) {
            logger.warn("Could not detect browser location, falling back to production", error);
        }

        return "production";
    }

    async _callServiceWithErrorHandling(domain, service, data = {}) {
        try {
            if (!this.hass) {
                throw new Error("Home Assistant instance is not available");
            }
            console.debug(domain, service, data)
            const result = await this.hass.callApi(
                "POST",
                `services/${domain}/${service}?return_response`,
                data
            );
            const apiMetadata = result?.api_metadata || {};
            logger.debug(`Service ${domain}.${service} called successfully`, { apiMetadata });
            const apiStatus = result?.api_status || 200;
            const apiMessage = result?.api_message || "Success";
            if (apiStatus !== 200) {
                logger.error(`Service ${domain}.${service} returned error status`, { apiStatus, apiMessage });
                throw new Error(`Service error: ${apiMessage} (status ${apiStatus})`);
            }
            return result;
        } catch (error) {
            logger.error(`Error while calling service ${service}`, error);
            throw new Error(`Home Assistant service error: ${error.message}`);
        }
    }
    async _callWSWithErrorHandling(message) {
        try {
            if (!this.hass) {
                throw new Error("Home Assistant instance is not available");
            }

            logger.debug("WS call started", message);

            const result = await this.hass.callWS(message);

            logger.debug("WS call succeeded", { result });

            return result;
        } catch (error) {
            logger.error("WS call failed", { message, error: error.message });
            throw new Error(`WebSocket error: ${error.message}`);
        }
    }
    async _fetchWithErrorHandling(url, options = {}) {
        try {
            logger.debug("HTTP request started", { url, method: options.method ?? "GET" });
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            logger.debug("HTTP request succeeded", { url, status: response.status });
            return await response.json();
        } catch (error) {
            logger.error("HTTP request failed", { url, error: error.message });
            throw new Error(`Internal error: ${error.message}`);
        }
    }
    async getTasks() {
        logger.info("Fetching tasks");
        if (this.environment === "development") {
            const url = `${this.baseUrl}/saviia/get_tasks?return_response`
            const data = await this._fetchWithErrorHandling(url, {
                method: 'POST',
                headers: this._hassHeaders
            })
            const tasks = data.service_response.api_metadata.tasks
            logger.info("Tasks fetched", { count: tasks.length });
            return tasks
        } else {
            const data = await this._callServiceWithErrorHandling('saviia', 'get_tasks')
            console.log(data)
            const tasks = data.service_response.api_metadata.tasks
            logger.info("Tasks fetched via hass service", tasks);
            return tasks
        }
    }

    async updateTask(task, completed) {
        logger.info("Updating task", { taskId: task?.tid, completed });
        const payload = { task: task, completed: completed };
        if (this.environment === "development") {
            const url = `${this.baseUrl}/saviia/update_task?return_response`
            const result = await this._fetchWithErrorHandling(url, {
                method: 'POST',
                headers: this._hassHeaders,
                body: JSON.stringify(payload)
            })
            logger.info('Task updated at Discord', { taskId: task?.tid })
            return result
        } else {
            const result = await this._callServiceWithErrorHandling('saviia', 'update_task', payload);
            logger.info('Task updated via hass service', { taskId: task?.tid }, result)
            return result;
        }
    }

    async deleteTask(taskId) {
        logger.info("Deleting task", { taskId });
        const payload = { task_id: taskId };
        if (this.environment === "development") {
            const url = `${this.baseUrl}/saviia/delete_task?return_response`
            const result = await this._fetchWithErrorHandling(url, {
                method: 'POST',
                headers: this._hassHeaders,
                body: JSON.stringify(payload)
            })
            logger.info('Task deleted at Discord', { taskId })
            return result
        } else {
            const result = await this._callServiceWithErrorHandling('saviia', 'delete_task', payload);
            logger.info('Task deleted via hass service', { taskId }, result)
            return result;
        }
    }

    async createTask(task, images = []) {
        logger.info("Creating task", { task });
        const payload = { task: task, images: images }
        if (this.environment === "development") {
            const url = `${this.baseUrl}/saviia/create_task?return_response`
            const result = await this._fetchWithErrorHandling(url, {
                method: 'POST',
                headers: this._hassHeaders,
                body: JSON.stringify(payload)
            })
            logger.info('Task created successfully at Discord', { task }, { images: images.length })
            return result
        } else {
            const result = await this._callServiceWithErrorHandling('saviia', 'create_task', payload);
            logger.info('Task created via hass service', { task }, result)
            return result;
        }
    }

    async getFailedSensors(localBackup, days) {
        logger.info("Fetching failed sensors", { localBackup, days });
        const payload = { local_backup_source_path: localBackup, n_days: days }
        if (this.environment === "development") {
            const url = `${this.baseUrl}/saviia/detect_failures?return_response`
            const result = await this._fetchWithErrorHandling(url, {
                method: 'POST',
                headers: this._hassHeaders,
                body: JSON.stringify(payload)
            })
            const sensors = result.service_response.api_metadata.validation
            logger.info('Failed sensors fetched at Discord', { count: sensors.length })
            return sensors
        } else {
            const result = await this._callServiceWithErrorHandling('saviia', 'detect_failures', payload);
            logger.info('Failed sensors fetched via hass service',
                { count: result.service_response.api_metadata.validation.length });
            return result;
        }
    }

    async getConfigFlowValue(key) {
        logger.info("Fetching config flow value", { key });
        const payload = { key }
        if (this.environment === "development") {
            const url = `${this.baseUrl}/saviia/get_config_value?return_response`
            const result = await this._fetchWithErrorHandling(url, {
                method: 'POST',
                headers: this._hassHeaders,
                body: JSON.stringify(payload)
            })
            const value = result.service_response.value
            logger.info('Config flow value fetched at Discord', { key, value });
            return value
        } else {
            const result = await this._callServiceWithErrorHandling('saviia', 'get_config_value', payload);
            const value = result.service_response.value
            logger.info('Config flow value fetched via hass service', { key, value });
            return value;
        }
    }
    async getPeople() {
        logger.info("Fetching people");

        if (this.environment === "development") {
            // 🔧 opción simple: mock temporal
            logger.warn("Using mock people in development");
            return [
                {
                    id: "juan",
                    name: "Juan Pérez",
                    email: "juan@mail.com",
                    discord: "juan#1234"
                },
                {
                    id: "ana",
                    name: "Ana Soto",
                    email: "ana@mail.com",
                    discord: null
                }
            ];
        } else {
            const people = await this._callWSWithErrorHandling({
                type: "saviia/get_people"
            });

            logger.info("People fetched via websocket", { count: people.length });

            return people;
        }
    }
}