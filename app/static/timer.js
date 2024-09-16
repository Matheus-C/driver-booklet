//window.app =
function stopwatch() {
  return {
    // States Functionality
    locationEnabled: false,
    isModalVisible: true,
    isModalAttachmentVisible: false,
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
        if (this.idVehicle !== null){
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

            });
        }
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
      if (!this.timerRunning && !this.isResting && !this.isEnd) {
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
      }else{
        if (this.isEnd || this.isResting) {
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

    setdiffBetweenTimestamps() {
      if (this.idVehicle !== null){
          fetch('/vehicle/rest/' + this.idVehicle, {
            method: 'GET',
            headers: {
              "Content-type": "application/json; charset=UTF-8"
            }
          }).then(response => response.json()).then(
              data => {
              let rest_time;
                if (data === {}){
                    const rest_time = 0;
                }else{
                    rest_time = data.total_rest_time*1000;
                    if(this.isResting){
                        if (rest_time === null){
                            rest_time = 0;
                        }
                        rest_time = rest_time + (new Date() - new Date(Date.parse(data.eventTime)));

                    }
                }
              const givenTime = new Date(Date.parse(data.last_start));
              const currentTime = new Date();
              console.log(currentTime);
              console.log(givenTime);
              const timeDifference = currentTime - givenTime - rest_time;
              const hoursDifference = Math.floor(timeDifference / (1000 * 60 * 60));
              const minutesDifference = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
              const secondsDifference = Math.floor((timeDifference % (1000 * 60)) / 1000);
              this.hours = hoursDifference;
              this.minutes = minutesDifference;
              this.seconds = secondsDifference;
              this.Timer();
          });
      }
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
        else if (mode === 'rest_start'){
            this.Timer();
        }
        else if (mode === 'day_end') {
          window.dispatchEvent(new CustomEvent("end"));
          this.Timer();
          this.isModalVisible = true;
          this.seconds = 0;
          this.minutes = 0;
          this.hours = 0;
        }
      }else {
        this.setdiffBetweenTimestamps()
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
      this.isEnd = false;
      this.currentActivityName = 'Atividade Atual';
      this.loadLastData();
      this.isModalVisible = true;
    },

    closeModal() {
      this.isModalVisible = false;
      if (!this.isEnd) {
        this.checkVisibilityPage();
        this.getUpdatesFromDB();
      }
    },

    openAttachmentForm(){
      this.isModalAttachmentVisible = true;
    },

    closeAttachmentForm(){
      this.isModalAttachmentVisible = false;
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
    loadLastData(){
            fetch('/timer/last_data', {
            method: 'GET',
            headers: {
              "Content-type": "application/json; charset=UTF-8"
            }
          }).then(response => response.json()).then(
            data => {
                if (data === {}){
                    this.idVehicle = "None";
                    this.idCompany = "None";
                }
                else{
                    this.idVehicle = data.idVehicle;
                    this.idCompany = data.idCompany;
                }

                window.dispatchEvent(new CustomEvent("loadLast",
                {detail: {idVehicle: this.idVehicle, idCompany: this.idCompany}}));
            }
          );
        },
  }
}
