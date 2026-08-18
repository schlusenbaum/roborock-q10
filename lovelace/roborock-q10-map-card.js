class RoborockQ10MapCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._card = null;
    this._config = null;
    this._hass = null;
    this._roomsKey = null;
    this._loading = false;
    this._timer = null;
  }

  setConfig(config) {
    if (!config.entity) throw new Error("entity is required");
    if (!config.map_source) throw new Error("map_source is required");

    this._config = structuredClone(config);

    if (this._hass) this._loadRooms();
  }

  set hass(hass) {
    const firstHass = !this._hass;
    this._hass = hass;

    if (this._card) {
      this._card.hass = hass;
    }

    if (firstHass && this._config) {
      this._loadRooms();

      this._timer = setInterval(
        () => this._loadRooms(),
        10000
      );
    }
  }

  get hass() {
    return this._hass;
  }

  async _loadRooms() {
    if (!this._hass || !this._config || this._loading) return;

    this._loading = true;

    try {
      const result = await this._hass.callWS({
        type: "roborock_q10/get_rooms",
        entity_id: this._config.entity,
      });

      const rooms = result.rooms || [];

      if (!rooms.length) return;

      const key = JSON.stringify(rooms);

      if (key === this._roomsKey) return;

      this._roomsKey = key;
      await this._renderCard(rooms);
    } catch (error) {
      console.error("Roborock Q10 Map Card:", error);
    } finally {
      this._loading = false;
    }
  }

  async _renderCard(rooms) {
    await customElements.whenDefined("xiaomi-vacuum-map-card");

    const selections = rooms.map(room => ({
      id: room.id,
      icon: {
        name: "mdi:broom",
        x: room.map_width - room.x,
        y: room.y,
      },
      label: {
        text: this._config.room_names?.[room.id] || room.name,
        x: room.map_width - room.x,
        y: room.y,
        offset_y: 35,
      },
    }));

    const config = structuredClone(this._config);
    delete config.type;

    const modes = config.map_modes || [];

    let roomMode = modes.find(
      mode => mode.name === "Rooms" ||
              mode.selection_type === "ROOM"
    );

    if (!roomMode) {
      roomMode = modes.find(
        mode => mode.template === "vacuum_clean_segment"
      );

      if (roomMode) {
        delete roomMode.template;
        roomMode.name = "Rooms";
        roomMode.icon = "mdi:floor-plan";
        roomMode.run_immediately = false;
        roomMode.selection_type = "ROOM";
        roomMode.id_type = "number";
        roomMode.max_selections = 999;
        roomMode.repeats_type = "EXTERNAL";
        roomMode.max_repeats = 3;
      }
    }

    if (!roomMode) {
      roomMode = {
        name: "Rooms",
        icon: "mdi:floor-plan",
        run_immediately: false,
        selection_type: "ROOM",
        id_type: "number",
        max_selections: 999,
        repeats_type: "EXTERNAL",
        max_repeats: 3,
      };

      modes.push(roomMode);
    }

    roomMode.predefined_selections = selections;

    roomMode.service_call_schema = {
      service: "vacuum.clean_segments",
      service_data: {
        entity_id: "[[entity_id]]",
        segment_ids: "[[selection]]",
      },
    };

    config.map_modes = modes;
    config.type = "custom:xiaomi-vacuum-map-card";

    if (this._card) {
      this._card.remove();
    }

    this._card = document.createElement(
      "xiaomi-vacuum-map-card"
    );

    this.shadowRoot.appendChild(this._card);

    this._card.setConfig(config);

    const mapStyle = document.createElement("style");
    mapStyle.textContent = `
      #map-zoomer-content {
        left: -30px;
      }

      #map-image {
        transform: scaleX(-1);
        transform-origin: center center;
      }
    `;
    this._card.shadowRoot.appendChild(mapStyle);

    this._card.hass = this._hass;
  }

  disconnectedCallback() {
    if (this._timer) {
      clearInterval(this._timer);
      this._timer = null;
    }
  }

  getCardSize() {
    return 8;
  }
}

customElements.define(
  "roborock-q10-map-card",
  RoborockQ10MapCard
);
