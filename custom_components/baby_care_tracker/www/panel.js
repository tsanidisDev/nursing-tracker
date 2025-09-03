import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit@2.0.0/index.js?module";

class BabyCareTrackerPanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      panel: { type: Object },
      _devices: { type: Array },
      _deviceActions: { type: Array },
      _selectedDevice: { type: Object },
      _selectedDeviceAction: { type: Object },
      _mappings: { type: Array },
      _loading: { type: Boolean },
      _babyCareActions: { type: Array }
    };
  }

  constructor() {
    super();
    this._devices = [];
    this._deviceActions = [];
    this._selectedDevice = null;
    this._selectedDeviceAction = null;
    this._mappings = [];
    this._loading = true;
    this._babyCareActions = [
      { key: 'feeding_start_left', label: 'Start Left Breast', icon: 'mdi:baby-bottle' },
      { key: 'feeding_start_right', label: 'Start Right Breast', icon: 'mdi:baby-bottle-outline' },
      { key: 'feeding_stop', label: 'Stop Feeding', icon: 'mdi:stop-circle' },
      { key: 'sleep_start', label: 'Start Sleep', icon: 'mdi:sleep' },
      { key: 'wake_up', label: 'Wake Up', icon: 'mdi:weather-sunny' },
      { key: 'diaper_pee', label: 'Pee Diaper', icon: 'mdi:water' },
      { key: 'diaper_poo', label: 'Poo Diaper', icon: 'mdi:emoticon-poop' },
      { key: 'diaper_both', label: 'Both Diaper', icon: 'mdi:baby-carriage' }
    ];
  }

  firstUpdated() {
    this._loadDevices();
    this._loadMappings();
  }

  async _loadDevices() {
    try {
      // Get all entities that are buttons, switches, etc.
      const relevantEntities = Object.values(this.hass.states).filter(entity => 
        ['button', 'switch', 'input_button', 'binary_sensor'].includes(entity.entity_id.split('.')[0])
      );
      
      console.log('Found relevant entities:', relevantEntities.length);
      
      // Try to get device registry
      let deviceRegistry = [];
      try {
        deviceRegistry = await this.hass.callWS({
          type: "config/device_registry/list",
        });
        console.log('Device registry loaded:', deviceRegistry.length, 'devices');
      } catch (err) {
        console.warn('Could not load device registry:', err);
      }
      
      // Group entities by device
      const deviceMap = new Map();
      
      for (const entity of relevantEntities) {
        try {
          // Try to get entity registry info
          const entityRegistry = await this.hass.callWS({
            type: "config/entity_registry/get",
            entity_id: entity.entity_id,
          });
          
          if (entityRegistry?.device_id) {
            const device = deviceRegistry.find(d => d.id === entityRegistry.device_id);
            if (device) {
              if (!deviceMap.has(device.id)) {
                deviceMap.set(device.id, {
                  id: device.id,
                  name: device.name_by_user || device.name || device.model || 'Unknown Device',
                  model: device.model,
                  manufacturer: device.manufacturer,
                  entities: []
                });
              }
              deviceMap.get(device.id).entities.push({
                entity_id: entity.entity_id,
                name: entity.attributes.friendly_name || entity.entity_id,
                domain: entity.entity_id.split('.')[0],
                state: entity.state
              });
            }
          } else {
            // Entity without device - create virtual device
            const domain = entity.entity_id.split('.')[0];
            const virtualDeviceId = `virtual_${domain}`;
            
            if (!deviceMap.has(virtualDeviceId)) {
              deviceMap.set(virtualDeviceId, {
                id: virtualDeviceId,
                name: `${domain.charAt(0).toUpperCase() + domain.slice(1)} Entities`,
                model: 'Virtual Device',
                manufacturer: 'Home Assistant',
                entities: []
              });
            }
            
            deviceMap.get(virtualDeviceId).entities.push({
              entity_id: entity.entity_id,
              name: entity.attributes.friendly_name || entity.entity_id,
              domain: entity.entity_id.split('.')[0],
              state: entity.state
            });
          }
        } catch (entityError) {
          console.warn('Error processing entity:', entity.entity_id, entityError);
          
          // Fallback: add to virtual device
          const domain = entity.entity_id.split('.')[0];
          const virtualDeviceId = `virtual_${domain}`;
          
          if (!deviceMap.has(virtualDeviceId)) {
            deviceMap.set(virtualDeviceId, {
              id: virtualDeviceId,
              name: `${domain.charAt(0).toUpperCase() + domain.slice(1)} Entities`,
              model: 'Virtual Device',
              manufacturer: 'Home Assistant',
              entities: []
            });
          }
          
          deviceMap.get(virtualDeviceId).entities.push({
            entity_id: entity.entity_id,
            name: entity.attributes.friendly_name || entity.entity_id,
            domain: entity.entity_id.split('.')[0],
            state: entity.state
          });
        }
      }
      
      this._devices = Array.from(deviceMap.values()).filter(device => device.entities.length > 0);
      console.log('Final devices:', this._devices);
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
    this._selectedDeviceAction = null; // Reset selected action
    
    if (this._selectedDevice) {
      await this._loadDeviceActions();
    } else {
      this._deviceActions = [];
    }
  }

  async _loadDeviceActions() {
    if (!this._selectedDevice) return;
    
    const actions = [];
    
    // For each entity in the device, get available actions
    for (const entity of this._selectedDevice.entities) {
      const entityActions = [];
      
      if (entity.domain === 'button') {
        // Try to get device-specific actions from device triggers
        const deviceTriggers = await this._getDeviceTriggers(this._selectedDevice.id);
        
        if (deviceTriggers.length > 0) {
          // Use device triggers if available
          for (const trigger of deviceTriggers) {
            if (trigger.entity_id === entity.entity_id || !trigger.entity_id) {
              entityActions.push({
                action: trigger.subtype || trigger.type,
                label: this._formatActionLabel(trigger.subtype || trigger.type),
                trigger: trigger
              });
            }
          }
        }
        
        // Always add generic button press option
        entityActions.push({
          action: 'press',
          label: 'Button Press (Any)',
          trigger: null
        });
      } else {
        // For switches, binary_sensors, input_buttons - state change triggers
        entityActions.push({
          action: 'state_change',
          label: 'State Change (On/Off)',
          trigger: null
        });
      }
      
      actions.push({
        entity_id: entity.entity_id,
        entity_name: entity.name,
        domain: entity.domain,
        actions: entityActions
      });
    }
    
    this._deviceActions = actions;
  }

  async _getDeviceTriggers(deviceId) {
    try {
      const deviceTriggers = await this.hass.callWS({
        type: "device_automation/trigger/list",
        device_id: deviceId,
      });
      return deviceTriggers || [];
    } catch (error) {
      console.log('No device triggers found for device:', deviceId);
      return [];
    }
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

  _getEntityIcon(domain) {
    const iconMap = {
      'button': 'mdi:gesture-tap-button',
      'switch': 'mdi:toggle-switch',
      'binary_sensor': 'mdi:checkbox-marked-circle',
      'sensor': 'mdi:chart-line',
      'input_boolean': 'mdi:toggle-switch-variant',
      'light': 'mdi:lightbulb'
    };
    return iconMap[domain] || 'mdi:help-circle';
  }

  _onDeviceActionClick(entityId, action, event) {
    // Store the selected device action
    this._selectedDeviceAction = { entity_id: entityId, action: action };
    
    // Visual feedback - remove previous selections and highlight this one
    const actionChips = this.shadowRoot.querySelectorAll('.action-chip');
    actionChips.forEach(chip => chip.classList.remove('selected'));
    
    if (event && event.target) {
      const clickedChip = event.target.closest('.action-chip');
      if (clickedChip) {
        clickedChip.classList.add('selected');
      }
    }
    
    console.log('Selected device action:', this._selectedDeviceAction);
  }

  _onBabyCareActionClick(actionKey) {
    if (!this._selectedDeviceAction) {
      this._showToast('Please select a device action first (click on a blue action chip above)');
      return;
    }

    this._addMapping(
      this._selectedDeviceAction.entity_id, 
      this._selectedDeviceAction.action, 
      actionKey
    );
  }

  _getMappingForAction(actionKey) {
    return this._mappings.find(m => m.action === actionKey);
  }

  _getMappingsForAction(actionKey) {
    return this._mappings.filter(m => m.action === actionKey);
  }

  async _removeMappingClick(event, mapping) {
    event.stopPropagation();
    await this._removeMapping(mapping);
  }

  _showToast(message) {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--primary-color);
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      z-index: 9999;
      font-size: 14px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 3000);
  }

  render() {
    if (this._loading) {
      return html`
        <div class="loading">
          <ha-circular-progress indeterminate></ha-circular-progress>
          <p>Loading devices and mappings...</p>
        </div>
      `;
    }

    return html`
      <div class="container">
        <div class="header">
          <h1>
            <ha-icon icon="mdi:baby-face"></ha-icon>
            Baby Care Tracker
          </h1>
          <p>Configure your smart devices to trigger baby care actions</p>
        </div>

        <div class="main-content">
          <!-- Device Selection Section -->
          <div class="section device-selection">
            <h2><ha-icon icon="mdi:devices"></ha-icon> Select Device</h2>
            <div class="device-picker">
              <select @change=${this._onDeviceSelected} .value=${this._selectedDevice?.id || ''}>
                <option value="">Choose a device...</option>
                ${this._devices.map(device => html`
                  <option value=${device.id}>
                    ${device.name} ${device.model ? `(${device.model})` : ''}
                  </option>
                `)}
              </select>
              ${this._selectedDevice ? html`
                <div class="device-info">
                  <h3>${this._selectedDevice.name}</h3>
                  <p>${this._selectedDevice.manufacturer || ''} ${this._selectedDevice.model || ''}</p>
                  <p><strong>${this._selectedDevice.entities.length}</strong> entities available</p>
                </div>
              ` : ''}
            </div>
          </div>

          <!-- Device Actions Section -->
          ${this._selectedDevice && this._deviceActions.length > 0 ? html`
            <div class="section device-actions">
              <h2><ha-icon icon="mdi:gesture-tap-button"></ha-icon> Available Device Actions</h2>
              <div class="device-entities">
                ${this._deviceActions.map(entityAction => html`
                  <div class="entity-card">
                    <h3>
                      <ha-icon icon=${this._getEntityIcon(entityAction.domain)}></ha-icon>
                      ${entityAction.entity_name}
                    </h3>
                    <div class="entity-actions">
                      ${entityAction.actions.map(action => html`
                        <div class="action-chip" 
                             @click=${(e) => this._onDeviceActionClick(entityAction.entity_id, action.action, e)}>
                          ${action.label}
                        </div>
                      `)}
                    </div>
                  </div>
                `)}
              </div>
            </div>
          ` : this._selectedDevice ? html`
            <div class="section">
              <p class="no-actions">No compatible actions found for this device.</p>
            </div>
          ` : ''}

          <!-- Baby Care Actions Section -->
          <div class="section baby-care-actions">
            <h2><ha-icon icon="mdi:baby"></ha-icon> Baby Care Actions</h2>
            <p class="instructions">Click on a device action above, then click on a baby care action below to create a mapping.</p>
            
            <div class="actions-grid">
              ${this._babyCareActions.map(action => html`
                <div class="action-card ${this._getMappingForAction(action.key) ? 'mapped' : ''}" 
                     @click=${() => this._onBabyCareActionClick(action.key)}>
                  <div class="action-header">
                    <ha-icon icon=${action.icon}></ha-icon>
                    <h3>${action.label}</h3>
                  </div>
                  
                  ${this._getMappingForAction(action.key) ? html`
                    <div class="current-mapping">
                      <p><strong>Currently mapped:</strong></p>
                      ${this._getMappingsForAction(action.key).map(mapping => html`
                        <div class="mapping-detail">
                          <span class="entity">${mapping.entity_id}</span>
                          ${mapping.specific_action ? html`
                            <span class="specific-action">(${mapping.specific_action})</span>
                          ` : ''}
                          <button class="remove-btn" @click=${(e) => this._removeMappingClick(e, mapping)}>
                            <ha-icon icon="mdi:close"></ha-icon>
                          </button>
                        </div>
                      `)}
                    </div>
                  ` : html`
                    <div class="no-mapping">
                      <p>No device mapped</p>
                      <p class="hint">Select a device action above, then click here</p>
                    </div>
                  `}
                </div>
              `)}
            </div>
          </div>

          <!-- Current Mappings Overview -->
          ${this._mappings.length > 0 ? html`
            <div class="section mappings-overview">
              <h2><ha-icon icon="mdi:link-variant"></ha-icon> All Current Mappings</h2>
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
                      <ha-icon icon="mdi:delete"></ha-icon>
                    </button>
                  </div>
                `)}
              </div>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  static get styles() {
    return css`
      :host {
        --primary-color: #03A9F4;
        --accent-color: #FF9800;
        --success-color: #4CAF50;
        --danger-color: #F44336;
        --card-background: var(--card-background-color, #ffffff);
        --text-primary: var(--primary-text-color, #212121);
        --text-secondary: var(--secondary-text-color, #757575);
        --divider-color: var(--divider-color, #e0e0e0);
      }

      .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        font-family: var(--paper-font-body1_-_font-family);
      }

      .header {
        text-align: center;
        margin-bottom: 32px;
        padding: 24px;
        background: linear-gradient(135deg, var(--primary-color), #0288D1);
        color: white;
        border-radius: 12px;
      }

      .header h1 {
        margin: 0 0 8px 0;
        font-size: 2.5rem;
        font-weight: 300;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
      }

      .header p {
        margin: 0;
        opacity: 0.9;
        font-size: 1.1rem;
      }

      .main-content {
        display: flex;
        flex-direction: column;
        gap: 24px;
      }

      .section {
        background: var(--card-background);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid var(--divider-color);
      }

      .section h2 {
        margin: 0 0 20px 0;
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 12px;
      }

      .device-picker select {
        width: 100%;
        padding: 12px 16px;
        border: 2px solid var(--divider-color);
        border-radius: 8px;
        font-size: 16px;
        background: var(--card-background);
        color: var(--text-primary);
        transition: border-color 0.3s ease;
      }

      .device-picker select:focus {
        outline: none;
        border-color: var(--primary-color);
      }

      .device-info {
        margin-top: 16px;
        padding: 16px;
        background: #f5f5f5;
        border-radius: 8px;
        border-left: 4px solid var(--primary-color);
      }

      .device-info h3 {
        margin: 0 0 8px 0;
        color: var(--text-primary);
      }

      .device-info p {
        margin: 4px 0;
        color: var(--text-secondary);
      }

      .device-entities {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }

      .entity-card {
        background: #f9f9f9;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid var(--divider-color);
      }

      .entity-card h3 {
        margin: 0 0 12px 0;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .entity-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      .action-chip {
        padding: 8px 16px;
        background: var(--primary-color);
        color: white;
        border-radius: 20px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        user-select: none;
      }

      .action-chip:hover {
        background: #0288D1;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(3, 169, 244, 0.3);
      }

      .action-chip.selected {
        background: var(--success-color);
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
      }

      .instructions {
        background: #e3f2fd;
        border: 1px solid #bbdefb;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 0 0 20px 0;
        color: #1565c0;
        font-style: italic;
      }

      .actions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 16px;
      }

      .action-card {
        background: var(--card-background);
        border: 2px solid var(--divider-color);
        border-radius: 12px;
        padding: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
      }

      .action-card:hover {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
      }

      .action-card.mapped {
        border-color: var(--success-color);
        background: #f1f8e9;
      }

      .action-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
      }

      .action-header ha-icon {
        font-size: 2.5rem;
        color: var(--primary-color);
      }

      .action-card.mapped .action-header ha-icon {
        color: var(--success-color);
      }

      .action-header h3 {
        margin: 0;
        font-size: 1.2rem;
        color: var(--text-primary);
      }

      .current-mapping {
        text-align: left;
      }

      .current-mapping p {
        margin: 0 0 8px 0;
        font-weight: 500;
        color: var(--text-primary);
      }

      .mapping-detail {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 4px 0;
        border: 1px solid var(--divider-color);
      }

      .mapping-detail .entity {
        font-family: monospace;
        background: #f5f5f5;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9rem;
      }

      .mapping-detail .specific-action {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-style: italic;
      }

      .remove-btn {
        background: var(--danger-color);
        color: white;
        border: none;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.3s ease;
      }

      .remove-btn:hover {
        background: #d32f2f;
      }

      .no-mapping {
        color: var(--text-secondary);
        font-style: italic;
      }

      .no-mapping .hint {
        font-size: 0.9rem;
        color: var(--primary-color);
      }

      .no-actions {
        text-align: center;
        color: var(--text-secondary);
        font-style: italic;
        padding: 20px;
      }

      .mappings-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .mapping-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        background: #f9f9f9;
        border-radius: 8px;
        border: 1px solid var(--divider-color);
      }

      .mapping-info {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;
      }

      .mapping-info strong {
        font-family: monospace;
        background: #f5f5f5;
        padding: 4px 8px;
        border-radius: 4px;
      }

      .mapping-info .specific-action {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-style: italic;
      }

      .mapping-info .arrow {
        color: var(--text-secondary);
        font-weight: bold;
      }

      .mapping-info .action {
        color: var(--primary-color);
        font-weight: 500;
      }

      .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 200px;
        color: var(--text-secondary);
      }

      .loading p {
        margin-top: 16px;
        font-size: 1.1rem;
      }

      @media (max-width: 768px) {
        .container {
          padding: 12px;
        }
        
        .actions-grid {
          grid-template-columns: 1fr;
        }
        
        .header h1 {
          font-size: 2rem;
        }
        
        .mapping-info {
          flex-direction: column;
          align-items: flex-start;
          gap: 8px;
        }
      }
    `;
  }
}

customElements.define("baby-care-tracker-panel", BabyCareTrackerPanel);
