plugins {
    id("org.jetbrains.intellij.platform") version "2.5.0"
}

repositories {
    mavenCentral()
    intellijPlatform {
        defaultRepositories()
    }
}

dependencies {
    intellijPlatform {
        create(providers.gradleProperty("platformType"), providers.gradleProperty("platformVersion"))
        instrumentationTools()
    }
}

intellijPlatform {
    pluginConfiguration {
        id = "com.weitingchen.suannhai-theme"
        name = "Suannhai Theme"
        version = providers.gradleProperty("pluginVersion")
        ideaVersion {
            sinceBuild = providers.gradleProperty("pluginSinceBuild")
            untilBuild = provider { null }
        }
        vendor {
            name = "WeitingChen"
            email = "72130405+WeiTing1991@users.noreply.github.com"
            url = "https://github.com/WeiTing1991/suannhai-theme"
        }
        description = """
            8 color themes inspired by Taiwanese and Japanese traditional colors.
            <br/><br/>
            <b>Formosa Collection (Taiwan):</b> Jiufen, Lâm-ní, Hue-pòo
            <br/>
            <b>Nippon Collection (Japan):</b> Rouiro, Sumi, Koiai, Torinoko, Shironeri
        """.trimIndent()
    }
}
