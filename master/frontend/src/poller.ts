export function poll<T>(
  fn: () => Promise<T>,
  shouldStop: (result: T) => boolean,
  interval: number
): Promise<T> {
  return new Promise((resolve, reject) => {
    let stopped = false;
    let timer: number | null = null;
    const pollFn = async () => {
      try {
        const result = await fn();
        if (shouldStop(result)) {
          stopped = true;
          if (timer) clearInterval(timer);
          resolve(result);
        }
      } catch (err) {
        stopped = true;
        if (timer) clearInterval(timer);
        reject(err);
      }
    };
    timer = window.setInterval(() => {
      if (!stopped) pollFn();
    }, interval);
    // Call immediately
    pollFn();
  });
}
