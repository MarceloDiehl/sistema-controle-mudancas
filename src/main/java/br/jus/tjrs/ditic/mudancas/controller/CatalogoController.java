package br.jus.tjrs.ditic.mudancas.controller;

import br.jus.tjrs.ditic.mudancas.dto.CatalogoDtos;
import br.jus.tjrs.ditic.mudancas.service.CatalogoService;
import br.jus.tjrs.ditic.mudancas.service.PrecoService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/** Catálogos e valores do custo. Alterar os valores é só do coordenador (SecurityConfig). */
@RestController
@RequestMapping("/api")
public class CatalogoController {

    private final CatalogoService catalogos;
    private final PrecoService precos;

    public CatalogoController(CatalogoService catalogos, PrecoService precos) {
        this.catalogos = catalogos;
        this.precos = precos;
    }

    @GetMapping("/catalogos")
    public CatalogoDtos.Catalogo catalogo() { return catalogos.catalogo(); }

    @GetMapping("/precos")
    public CatalogoDtos.Precos precos() { return precos.precos(); }

    @PutMapping("/precos")
    public Map<String, Integer> salvarPrecos(@RequestBody CatalogoDtos.Precos req) {
        return Map.of("alterados", precos.salvar(req));
    }
}
