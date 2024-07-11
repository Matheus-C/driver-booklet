//window.app = 
function stopwatch() {
  return {
    // States Functionality
    locationEnabled: false,
    isModalVisible: true,
    coords: { lat: 0, lon: 0 },
    stringCoords: null,
    timerRunning: false,

    // Vars
    idCompany: null,
    idVehicle: null,
    seconds: 0,
    minutes: 0,
    hours: 0,
    currentActivityName: 'Atividade Atual',

    // States
    isAvailable: false,
    isWorking: false,
    isResting: false,
    isEnd: false,

    getUpdatesFromDB() {
      fetch('/vehicle/last_state/' + this.idVehicle, {
        method: 'GET',
        headers: {
          "Content-type": "application/json; charset=UTF-8"
        }
      }).then(response => response.json()).then(
        data => {
          if (data.eventName != 'day_end') {
            this.updateTimer(data.eventName, data.eventTime);
          }

        }
      );
    },

    checkVisibilityPage() {
      const handler = () => {
        const isVisible = !document.hidden;
        if (isVisible) {
          this.getUpdatesFromDB();
        }
      }
      document.removeEventListener('visibilitychange', handler);
      document.addEventListener('visibilitychange', handler);
    },

    Timer() {
      if (!this.timerRunning) {
        this.timerRunning = true;
        this.timer = setInterval(() => {
          this.seconds++;
          if (this.seconds === 60) {
            this.seconds = 0;
            this.minutes++;
          }
          if (this.minutes === 60) {
            this.minutes = 0;
            this.hours++;
          }
        }, 1000);
      }
      else {
        if (this.isEnd) {
          clearInterval(this.timer);
          this.timerRunning = false;
        }
      }
    },

    get formattedTime() {
      let currentTime = String(this.hours).padStart(2, '0') + ':' +
        String(this.minutes).padStart(2, '0') + ':' +
        String(this.seconds).padStart(2, '0');
      return (
        currentTime
      );
    },

    setdiffBetweenTimestamps(timestamp) {
      const givenTime = new Date(Date.parse(timestamp));
      const currentTime = new Date();
      const timeDifference = currentTime - givenTime;
      const hoursDifference = Math.floor(timeDifference / (1000 * 60 * 60));
      const minutesDifference = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
      const secondsDifference = Math.floor((timeDifference % (1000 * 60)) / 1000);
      this.hours = hoursDifference;
      this.minutes = minutesDifference;
      this.seconds = secondsDifference;
      this.Timer();
    },

    updateTimer(mode, event_time) {
      config = {
        'availability_start': [{ isAvailable: true }, { isWorking: false }, { isResting: false }, { isEnd: false }],
        'work_start': [{ isWorking: true }, { isAvailable: false }, { isResting: false }, { isEnd: false }],
        'rest_start': [{ isResting: true }, { isWorking: false }, { isAvailable: false }, { isEnd: false }],
        'day_end': [{ isEnd: true }, { isResting: false }, { isWorking: false }, { isAvailable: false }],
      }
      config[mode].forEach(element => {
        const propertyName = Object.keys(element)[0];
        this[propertyName] = element[propertyName];
      });
      if (!event_time) {
        if (mode === 'availability_start') {
          this.Timer();
        }
        else if (mode === 'day_end') {
          this.Timer();
          this.isModalVisible = true;
          this.seconds = 0;
          this.minutes = 0;
          this.hours = 0;
        }
      }
      else {
        this.setdiffBetweenTimestamps(event_time)
      }
      this.setActivityName(mode)
    },

    setActivityName(mode) {
      config = {
        'availability_start': 'Disponível',
        'work_start': 'Trabalhando',
        'rest_start': 'Descansando',
        'day_end': 'Sessão Finalizada',
      }
      this.currentActivityName = config[mode];
    },

    openModal() {
      this.isModalVisible = true;
      this.isEnd = false;
      this.currentActivityName = 'Atividade Atual';
    },

    closeModal() {
      this.isModalVisible = false;
      if (!this.isEnd) {
        this.checkVisibilityPage();
        this.getUpdatesFromDB();
      }
    },

    askAttachment(){
      if(!this.isEnd){
        this.closeModal();
      }else{
        const newAttachment = confirm("Gostaria de adicionar uma observação?");
        if(newAttachment){
          htmx.ajax('GET', '/attachment/new', '#modal')
        }else{
          this.closeModal();
        }
      }
    },

    getLocationText() {
      this.stringCoords = this.coords.lat + ',' + this.coords.lon;
    },

    enableLocation() {
      navigator.geolocation.watchPosition((position) => {
        const newCoords = { lat: position.coords.latitude, lon: position.coords.longitude };
        if (this.isAvailable && this.distance_ari(this.coords, newCoords) >= 0.00003) { // Only start timer after initial location
          // In case of any gps movement will auto start working
          if (this.idCompany && this.idVehicle && this.isModalVisible === false) {
            document.querySelector('body').dispatchEvent(
              new Event('start_working')
            )
            this.Timer();
          }
          this.coords = newCoords;
        }
        else {
          this.coords = newCoords;
        }
      });
      this.locationEnabled = true;
      this.getLocationText();
    },

    distance_ari(coord1, coord2) {
      let pow_lat = Math.pow((coord1.lat - coord2.lat), 2)
      let pow_lon = Math.pow((coord1.lon - coord2.lon), 2)
      let d = Math.sqrt(pow_lat + pow_lon)
      return d
    },

  }
}
