import mitt from 'mitt';

const emitter = mitt();

export const EventBus = {
  on: emitter.on,
  off: emitter.off,
  emit: emitter.emit,
};
