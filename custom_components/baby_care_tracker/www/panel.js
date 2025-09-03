import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit@2.0.0/index.js?module";

class BabyCareTrackerPanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      _devices: { type: Array },
      _selectedDevice: { type: Object },
      _deviceActions: { type: Array },
      _mappings: { type: Array },
      _loading: { type: Boolean },
    };
  }

  constructor() {
    super();
    this._devices = [];
    this._selectedDevice = null;
    this._deviceActions = [];
    this._mappings = [];
    this._loading = true;
  }

  firstUpdated() {
    this._loadDevices();
    this._loadMappings();
  }

  async _loadDevices() {
    try {
      // Get devices that have button/switch entities
      const entities = Object.values(this.hass.states).filter(entity => 
        ['button', 'switch', 'input_button', 'binary_sensor'].includes(entity.entity_id.split('.')[0])
      );
      
      const deviceRegistry = await this.hass.callWS({
        type: "config/device_registry/list",
      });
      
      // Group entities by device
      const deviceMap = new Map();
      
      for (const entity of entities) {
        const entityRegistry = await this.hass.callWS({
          type: "config/entity_registry/get",
          entity_id: entity.entity_id,
        });
        
        if (entityRegistry?.device_id) {
          const device = deviceRegistry.find(d => d.id === entityRegistry.device_id);
          if (device) {
            if (!deviceMap.has(device.id)) {
              deviceMap.set(device.id, {
                ...device,
                entities: []
              });
            }
            deviceMap.get(device.id).entities.push({
              entity_id: entity.entity_id,
              name: entity.attributes.friendly_name || entity.entity_id,
              domain: entity.entity_id.split('.')[0]
            });
          }
        }
      }
      
      this._devices = Array.from(deviceMap.values()).filter(device => device.entities.length > 0);
      this._loading = false;
    } catch (error) {
      console.error('Error loading devices:', error);
      this._loading = false;
    }
  }

  async _loadMappings() {
    try {
      // Load current mappings from integration config
      const configEntries = await this.hass.callWS({
        type: "config_entries/get",
        domain: "baby_care_tracker",
      });
      
      if (configEntries.length > 0) {
        const config = configEntries[0];
        this._mappings = this._parseMappingsFromOptions(config.options);
      }
    } catch (error) {
      console.error('Error loading mappings:', error);
    }
  }

  _parseMappingsFromOptions(options) {
    const mappings = [];
    const actionMap = {
      'feeding_start_left_entity': 'Start Left Breast Feeding',
      'feeding_start_right_entity': 'Start Right Breast Feeding',
      'feeding_stop_entity': 'Stop Feeding',
      'sleep_start_entity': 'Start Sleep',
      'wake_up_entity': 'Wake Up',
      'diaper_pee_entity': 'Log Pee Diaper',
      'diaper_poo_entity': 'Log Poo Diaper',
      'diaper_both_entity': 'Log Both (Pee & Poo)',
    };

    for (const [configKey, entityConfig] of Object.entries(options)) {
      if (actionMap[configKey] && entityConfig) {
        const [entityId, specificAction] = entityConfig.includes(':') 
          ? entityConfig.split(':') 
          : [entityConfig, null];
        
        mappings.push({
          entity_id: entityId,
          action: actionMap[configKey],
          specific_action: specificAction,
          config_key: configKey
        });
      }
    }
    
    return mappings;
  }

  async _onDeviceSelected(event) {
    const deviceId = event.target.value;
    this._selectedDevice = this._devices.find(d => d.id === deviceId);
    
    if (this._selectedDevice) {
      await this._loadDeviceActions();
    }
  }

  async _loadDeviceActions() {
    if (!this._selectedDevice) return;
    
    const actions = [];
    
    // For each entity in the device, get available actions
    for (const entity of this._selectedDevice.entities) {
      if (entity.domain === 'button') {
        // Try to get device-specific actions from ZHA/deCONZ
        actions.push({
          entity_id: entity.entity_id,
          entity_name: entity.name,
          actions: await this._getButtonActions(entity.entity_id)
        });
      } else {
        // For switches, binary_sensors, input_buttons - state change triggers
        actions.push({
          entity_id: entity.entity_id,
          entity_name: entity.name,
          actions: [{ action: 'state_change', label: 'State Change' }]
        });
      }
    }
    
    this._deviceActions = actions;
  }

  async _getButtonActions(entityId) {
    // Try to get button-specific actions from device triggers
    try {
      const deviceTriggers = await this.hass.callWS({
        type: "device_automation/trigger/list",
        device_id: this._selectedDevice.id,
      });
      
      const buttonTriggers = deviceTriggers.filter(trigger => 
        trigger.entity_id === entityId || trigger.subtype
      );
      
      if (buttonTriggers.length > 0) {
        return buttonTriggers.map(trigger => ({
          action: trigger.subtype || trigger.type,
          label: this._formatActionLabel(trigger.subtype || trigger.type)
        }));
      }
    } catch (error) {
      console.log('No device triggers found, using default actions');
    }
    
    // Default button actions
    return [
      { action: 'press', label: 'Button Press' },
      { action: 'state_change', label: 'Any State Change' }
    ];
  }

  _formatActionLabel(action) {
    return action
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }

  async _addMapping(entityId, triggerAction, babyCareAction) {
    if (!entityId || !babyCareAction) return;
    
    // Call service to update mapping
    await this.hass.callService('baby_care_tracker', 'update_button_mapping', {
      entity_id: entityId,
      trigger_action: triggerAction === 'state_change' ? null : triggerAction,
      baby_care_action: babyCareAction
    });
    
    // Reload mappings
    await this._loadMappings();
    
    // Clear selection
    this._selectedDevice = null;
    this._deviceActions = [];
  }

  async _removeMapping(mapping) {
    await this.hass.callService('baby_care_tracker', 'remove_button_mapping', {
      entity_id: mapping.entity_id,
      specific_action: mapping.specific_action
    });
    
    await this._loadMappings();
  }

  render() {
    if (this._loading) {
      return html`
        <div class="loading">
          <ha-circular-progress indeterminate></ha-circular-progress>
          <p>Loading devices...</p>
        </div>
      `;
    }

    return html`
      <div class="container">
        <div class="header">
          <h1>
            <ha-icon icon="mdi:baby-face"></ha-icon>
            Baby Care Tracker - Button Mapping
          </h1>
          <p>Configure your smart buttons and switches to trigger baby care actions</p>
        </div>

        <div class="section">
          <h2>Add New Mapping</h2>
          <div class="mapping-builder">
            <div class="step">
              <h3>1. Select Device</h3>
              <select @change=${this._onDeviceSelected} .value=${this._selectedDevice?.id || ''}>
                <option value="">Choose a device...</option>
                ${this._devices.map(device => html`
                  <option value=${device.id}>
                    ${device.name || device.model || 'Unknown Device'}
                  </option>
                `)}
              </select>
            </div>

            ${this._selectedDevice ? html`
              <div class="step">
                <h3>2. Configure Actions</h3>
                ${this._deviceActions.map(entityAction => html`
                  <div class="entity-config">
                    <h4>${entityAction.entity_name}</h4>
                    ${entityAction.actions.map(action => html`
                      <div class="action-row">
                        <span class="trigger">${action.label}</span>
                        <span class="arrow">→</span>
                        <select class="baby-action" data-entity=${entityAction.entity_id} data-action=${action.action}>
                          <option value="">Select baby care action...</option>
                          <option value="feeding_start_left">Start Left Breast Feeding</option>
                          <option value="feeding_start_right">Start Right Breast Feeding</option>
                          <option value="feeding_stop">Stop Feeding</option>
                          <option value="sleep_start">Start Sleep</option>
                          <option value="wake_up">Wake Up</option>
                          <option value="diaper_pee">Log Pee Diaper</option>
                          <option value="diaper_poo">Log Poo Diaper</option>
                          <option value="diaper_both">Log Both (Pee & Poo)</option>
                        </select>
                        <button 
                          @click=${() => this._addMappingFromRow(entityAction.entity_id, action.action)}
                          class="add-btn"
                        >
                          Add
                        </button>
                      </div>
                    `)}
                  </div>
                `)}
              </div>
            ` : ''}
          </div>
        </div>

        <div class="section">
          <h2>Current Mappings</h2>
          ${this._mappings.length === 0 ? html`
            <p class="no-mappings">No button mappings configured yet.</p>
          ` : html`
            <div class="mappings-list">
              ${this._mappings.map(mapping => html`
                <div class="mapping-item">
                  <div class="mapping-info">
                    <strong>${mapping.entity_id}</strong>
                    ${mapping.specific_action ? html`
                      <span class="specific-action">(${mapping.specific_action})</span>
                    ` : ''}
                    <span class="arrow">→</span>
                    <span class="action">${mapping.action}</span>
                  </div>
                  <button 
                    @click=${() => this._removeMapping(mapping)}
                    class="remove-btn"
                  >
                    Remove
                  </button>
                </div>
              `)}
            </div>
          `}
        </div>
      </div>
    `;
  }

  _addMappingFromRow(entityId, triggerAction) {
    const select = this.shadowRoot.querySelector(`select[data-entity="${entityId}"][data-action="${triggerAction}"]`);
    const babyCareAction = select.value;
    
    if (babyCareAction) {
      this._addMapping(entityId, triggerAction, babyCareAction);
      select.value = '';
    }
  }

  static get styles() {
    return css`
      .container {
        padding: 20px;
        max-width: 1200px;
        margin: 0 auto;
      }

      .header {
        text-align: center;
        margin-bottom: 30px;
      }

      .header h1 {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        color: var(--primary-color);
      }

      .section {
        background: var(--card-background-color);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: var(--ha-card-box-shadow);
      }

      .mapping-builder {
        max-width: 800px;
      }

      .step {
        margin-bottom: 20px;
        padding: 15px;
        border: 1px solid var(--divider-color);
        border-radius: 8px;
      }

      .step h3 {
        margin-top: 0;
        color: var(--primary-color);
      }

      select {
        width: 100%;
        padding: 8px;
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
      }

      .entity-config {
        margin-bottom: 15px;
        padding: 10px;
        border-left: 3px solid var(--primary-color);
        background: var(--secondary-background-color);
      }

      .action-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
      }

      .trigger {
        min-width: 150px;
        font-weight: bold;
      }

      .arrow {
        color: var(--primary-color);
        font-size: 18px;
      }

      .baby-action {
        flex: 1;
      }

      .add-btn, .remove-btn {
        padding: 6px 12px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
      }

      .add-btn {
        background: var(--primary-color);
        color: white;
      }

      .remove-btn {
        background: var(--error-color);
        color: white;
      }

      .mappings-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
      }

      .mapping-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        border: 1px solid var(--divider-color);
        border-radius: 8px;
        background: var(--secondary-background-color);
      }

      .mapping-info {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .specific-action {
        color: var(--secondary-text-color);
        font-style: italic;
      }

      .action {
        color: var(--primary-color);
        font-weight: bold;
      }

      .no-mappings {
        text-align: center;
        color: var(--secondary-text-color);
        font-style: italic;
      }

      .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 200px;
        gap: 10px;
      }
    `;
  }
}

customElements.define("baby-care-tracker-panel", BabyCareTrackerPanel);
