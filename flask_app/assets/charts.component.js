console.error('hello')

class ChartElement extends HTMLElement {
  #canvas = null;
  #chart = null;
  connected = false;

  static get observedAttributes() {
    return ["config"];
  }

  constructor() {
    // Always call super first in constructor
    super();

    const shadow = this.attachShadow({ mode: "open" });

    const d = document.createElement('div');
    d.style="width: 100%; height: 100%; position: relative;";

    this.#canvas = document.createElement("canvas");
    d.appendChild(this.#canvas);
    shadow.appendChild(d);
  }

  connectedCallback() {
    console.log("Custom square element added to page.");
    this.connected = true;
    this.updateChart();
  }

  disconnectedCallback() {
    console.log("Custom square element removed from page.");
  }

  adoptedCallback() {
    console.log("Custom square element moved to new page.");
  }

  attributeChangedCallback(name, oldValue, newValue) {
    console.log("Custom square element attributes changed.");
    this.updateChart();
  }

  updateChart() {
    if(!this.connected) {
      return;
    }
    const config = JSON.parse(this.getAttribute('config'));
    if (!this.#chart) {
      this.#chart = new Chart(this.#canvas, config);
    } else {
      this.#chart.data = config.data ?? {};
      this.#chart.options = config.options ?? {};
      this.#chart.type = config.type;
      this.#chart.update('none');
    }
  }
}

customElements.define("charts-js", ChartElement);
console.log('defined');



