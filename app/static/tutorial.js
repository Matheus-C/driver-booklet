
const tourModalTimer = new Shepherd.Tour({
    defaultStepOptions: {
      cancelIcon: {
        enabled: true
      },
      classes: '',
      scrollTo: { behavior: 'smooth', block: 'center' }
    }
  });

  tourModalTimer.addStep({
    title: 'Selecione a empresa',
    text: 'Para iniciar selecione a empresa que você deseja.',
    attachTo: {
      element: '#selectCompany',
      on: 'top'
    },
    buttons: [
      {
        action() {
          return this.back();
        },
        classes: 'shepherd-button-secondary',
        text: 'Voltar'
      },
      {
        action() {
          return this.next();
        },
        text: 'Próximo'
      }
    ],
    id: 'selectCompany'
  });

  tourModalTimer.addStep({
    title: 'Selecionar veículo',
    text: 'Agora selecione o carro que você deseja.',
    attachTo: {
      element: '#selectVehicle',
      on: 'top'
    },
    buttons: [
      {
        action() {
          return this.back();
        },
        classes: 'shepherd-button-secondary',
        text: 'Voltar'
      },
      {
        action() {
          return this.next();
        },
        text: 'Próximo'
      }
    ],
    id: 'selectCar'
  });

  tourModalTimer.addStep({
    title: 'Quilometragem',
    text: 'Agora selecione a quilometragem atual do veículo.',
    attachTo: {
      element: '#mileage',
      on: 'top'
    },
    buttons: [
      {
        action() {
          return this.back();
        },
        classes: 'shepherd-button-secondary',
        text: 'Voltar'
      },
      {
        action() {
          return this.next();
        },
        text: 'Fechar'
      }
    ],
    id: 'mileage'
  });

  tourModalTimer.start();