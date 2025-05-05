// Nombre de la caché y versión - incrementa la versión cuando hagas cambios
const CACHE_NAME = 'sillage-pwa-v1';

// Recursos a pre-cachear (assets esenciales para la aplicación)
const urlsToCache = [
  // Rutas principales
  '/',
  '/es/recomendador/',
  '/es/perfumes/',
  '/es/usuarios/perfil/',
  
  // Assets estáticos clave
  '/static/img/logo.png',
  '/static/img/icons/icon-128x128.png',
  '/static/img/icons/icon-192x192.png',
  '/static/img/icons/icon-512x512.png',
  
  // CSS y JavaScript externos
  'https://cdn.tailwindcss.com',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css',
  
  // Offline fallback
  '/static/offline.html'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .catch(error => {
        console.error('Error durante la pre-caché:', error);
      })
  );
});

// Activación del Service Worker
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            // Borrar cachés antiguas
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Estrategia de caché para las peticiones: Cache First, luego Red
self.addEventListener('fetch', event => {
  // Ignora peticiones a Google Maps u otros servicios externos importantes
  if (event.request.url.includes('maps.googleapis.com') || 
      event.request.url.includes('googleapis.com') ||
      event.request.url.includes('openweathermap.org')) {
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Devuelve la respuesta cacheada si existe
        if (response) {
          return response;
        }
        
        // Si no está en caché, solicitarla a la red
        return fetch(event.request)
          .then(networkResponse => {
            // Si la red falla o no hay respuesta, no cachear
            if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
              return networkResponse;
            }
            
            // Clonar la respuesta para usar una versión en la caché y otra para el navegador
            const responseToCache = networkResponse.clone();
            
            caches.open(CACHE_NAME)
              .then(cache => {
                // Añadir el recurso a la caché
                cache.put(event.request, responseToCache);
              });
              
            return networkResponse;
          })
          .catch(error => {
            // Si la red falla para HTML, mostrar la página offline
            if (event.request.destination === 'document') {
              return caches.match('/static/offline.html');
            }
            
            console.error('Error en fetch:', error);
            // Aquí podrías devolver un recurso de fallback para imágenes, etc.
          });
      })
  );
});

// Sincronización en segundo plano (opcional)
self.addEventListener('sync', event => {
  if (event.tag === 'sync-recomendaciones') {
    // Código para sincronizar recomendaciones pendientes
    event.waitUntil(syncRecomendaciones());
  }
});

// Función para sincronizar datos (implementación ficticia)
function syncRecomendaciones() {
  // Esta función se activaría cuando se restaura la conexión
  console.log('Sincronizando datos pendientes...');
  return Promise.resolve();
}