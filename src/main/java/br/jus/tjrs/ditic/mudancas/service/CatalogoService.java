package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.dto.CatalogoDtos;
import br.jus.tjrs.ditic.mudancas.model.Servico;
import br.jus.tjrs.ditic.mudancas.repository.EmpresaRepository;
import br.jus.tjrs.ditic.mudancas.repository.LocalRepository;
import br.jus.tjrs.ditic.mudancas.repository.ServicoRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/** Locais, empresas e serviços, como estão no banco. */
@Service
@Transactional(readOnly = true)
public class CatalogoService {

    private final LocalRepository locais;
    private final EmpresaRepository empresas;
    private final ServicoRepository servicos;

    public CatalogoService(LocalRepository locais, EmpresaRepository empresas, ServicoRepository servicos) {
        this.locais = locais;
        this.empresas = empresas;
        this.servicos = servicos;
    }

    public CatalogoDtos.Catalogo catalogo() {
        Map<Long, List<String>> porEmpresa = servicos.listarComEmpresa().stream()
                .collect(Collectors.groupingBy(s -> s.getEmpresa().getId(), Collectors.mapping(Servico::getNome, Collectors.toList())));
        return new CatalogoDtos.Catalogo(
                locais.findAllByOrderByNomeAsc().stream().map(l -> new CatalogoDtos.Local(l.getNome(), l.getTipo().name(), l.getRegiao())).toList(),
                empresas.findAllByOrderByNomeAsc().stream()
                        .map(e -> new CatalogoDtos.Empresa(e.getNome(), e.isPagaPorServico(), porEmpresa.getOrDefault(e.getId(), List.of()))).toList());
    }
}
