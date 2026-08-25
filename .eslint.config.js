export default [
    {
        languageOptions: {
            ecmaVersion: 2020,
            globals: {
                document: "readonly",
                window: "readonly",
                fetch: "readonly",
                history: "readonly",
                location: "readonly",
                DOMParser: "readonly",
                DATA: "readonly",
            },
        },
        rules: {
            "no-unused-vars": "warn",
        },
    },
];
