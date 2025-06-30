import { setupLanguageSelector } from "../lang.js";

setupLanguageSelector({
    langSelectorId: 'langSelect',
    elements: ['title', 'nav_home', 'nav_yacht', 'nav_power', 'nav_mission'],
    defaultLang: 'en',
    apiUrlBase: '/api/translations',
    section: 'nav'
});

setupLanguageSelector({
    langSelectorId: 'langSelect',
    elements: [
        'addWaypoint',
        'delete',
        'save_as',
        'saveToPixhawk',
        'saveToRaspberryPi',
        'missionName',
        'confirmSaveToRaspberryPi',
        'closeSavePopup',
        'closePopup',
        'YachtControl',
        'createMission',
        'fetchMission',
        'saveMission',
        'setHome',
        'stopMission',
        'YachtInfo',
        'location',
        'speed',
        'direction',
        'depth',
        'wind_speed',
        'engine',
        'select',
        'missionlist',
        'name',
        'day',
        'action'
    ],
    defaultLang: 'en',
    apiUrlBase: '/api/translations',
    section: 'home'
});

setupLanguageSelector({
    langSelectorId: 'langSelect',
    elements: ['lat','lon','roll','pitch'],
    defaultLang: 'en',
    apiUrlBase: '/api/translations',
    section: 'yacht'
});

setupLanguageSelector({
    langSelectorId: 'langSelect',
    elements: [
        'time-operating',
        'remaining-time',
        'power-output',
        'engine-speed',
        'angel',
        'auto-update',
        'send_command',
        'control'
    ],
    defaultLang: 'en',
    apiUrlBase: '/api/translations',
    section: 'power'
});
