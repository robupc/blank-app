import time
import streamlit as st
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import random

# ノードクラスの定義（省略部分は元のコードと同じ）
@dataclass
class Node:
    name: str
    position_number: int
    bank_number: int = 0
    active: bool = True
    parent_node: Optional[str] = None
    tree_number: int = 0
    title_rank: int = 0
    past_title_rank: int = 0
    paid_point: int = 0
    bonus_point: int = 0
    total_paid_point: int = 0
    total_bonus_point: int = 0
    children: List['Node'] = field(default_factory=list)
    binary_number_1: int = 0
    binary_number_3: int = 0
    binary_number_5: int = 0
    binary_number_7: int = 0

    def process_bank_number(self, node1: 'Node', node2: 'Node') -> None:
        if not node1 or not node2:
            return
        tree1 = node1.tree_number
        tree2 = node2.tree_number
        if tree1 != tree2:
            while self.bank_number > 0 and tree2 < tree1:
                tree2 += 1
                self.bank_number -= 1
            diff = min(tree1 - tree2, 2)
            if diff > 0:
                self.bank_number = min(self.bank_number + diff, 2)

    def calculate_binary_numbers(self) -> None:
        active_children = sorted(
            [child for child in self.children if child.active],
            key=lambda x: x.tree_number,
            reverse=True
        )
        if not active_children:
            return

        if self.position_number >= 1 and len(active_children) >= 2:
            node1, node2 = active_children[0:2]
            self.binary_number_1 = (min(node1.tree_number, node2.tree_number) - 1) * 2
            self.process_bank_number(node1, node2)

        if self.position_number >= 3 and len(active_children) >= 4:
            node3, node4 = active_children[2:4]
            self.binary_number_3 = (min(node3.tree_number, node4.tree_number) - 1) * 2
            self.process_bank_number(node3, node4)

        if self.position_number >= 5 and len(active_children) >= 6:
            node5, node6 = active_children[4:6]
            self.binary_number_5 = (min(node5.tree_number, node6.tree_number) - 1) * 2
            self.process_bank_number(node5, node6)

        if self.position_number >= 7 and len(active_children) >= 8:
            node7, node8 = active_children[6:8]
            self.binary_number_7 = (min(node7.tree_number, node8.tree_number) - 1) * 2
            self.process_bank_number(node7, node8)

    def activate(self, active_prop) -> None:
        _active_prop = (100 - active_prop) / 100
        self.active = False
        self.active = random.random() > _active_prop

    def set_position(self, position: int) -> None:
        position_costs = {1: 41580, 3: 82060, 5: 122540, 7: 163020}
        if self.active:
            self.position_number = position
            self.paid_point = position_costs[position]
            self.total_paid_point += position_costs[position]

    def calculate_tree_number(self,nodes) -> int:
        #self.tree_number += 1
        #for child in self.children:
        #    if child.active:
        #        self.tree_number += 1
        #    else:
        #        self.tree_number -= 1
        #    child.calculate_tree_number()
        
        #self.tree_number += 1
        #for node in nodes:
        #    if self.name == node.parent_node:
        #        self.tree_number += 1
        #        node.calculate_tree_number(nodes)

        if not self.active:
            self.tree_number = 0
            return 0
        self.tree_number = 1
        for child in self.children:
            self.tree_number += child.calculate_tree_number(nodes)
        return self.tree_number

    def update_title_rank(self) -> None:
        active_children = len([child for child in self.children if child.active])
        rank_conditions = [
            (20, 2, 1), (60, 3, 2), (200, 4, 3),
            (600, 5, 4), (1000, 7, 5), (2000, 10, 6),
            (4000, 10, 7), (6000, 10, 8), (10000, 10, 9),
            (20000, 10, 10)
        ]
        self.past_title_rank = self.title_rank
        self.title_rank = 0
        for tree_req, children_req, rank in rank_conditions:
            if self.tree_number >= tree_req and active_children >= children_req:
                self.title_rank = rank

    def calculate_riseup_binary_bonus(self, bonus_params: Dict[str, float]) -> int:
        def calculate_bonus_for_binary(binary_number: int) -> float:
            if 4 <= binary_number <= 60:
                return bonus_params["level1"] * binary_number / 4
            elif 64 <= binary_number <= 200:
                return bonus_params["level1"] * 15 + bonus_params["level2"] * (binary_number - 60) / 4
            elif 204 <= binary_number <= 2000:
                return bonus_params["level1"] * 15 + bonus_params["level2"] * 35 + bonus_params["level3"] * (binary_number - 200) / 4
            elif 2004 <= binary_number <= 20000:
                return bonus_params["level1"] * 15 + bonus_params["level2"] * 35 + bonus_params["level3"] * 450 + bonus_params["level4"] * (binary_number - 2000) / 4
            elif binary_number > 20000:
                return bonus_params["level1"] * 15 + bonus_params["level2"] * 35 + bonus_params["level3"] * 450 + bonus_params["level4"] * 4500
            return 0
        bonus = 0
        if self.position_number >= 1:
            bonus += calculate_bonus_for_binary(self.binary_number_1)
        if self.position_number >= 3:
            bonus += calculate_bonus_for_binary(self.binary_number_3)
        if self.position_number >= 5:
            bonus += calculate_bonus_for_binary(self.binary_number_5)
        if self.position_number >= 7:
            bonus += calculate_bonus_for_binary(self.binary_number_7)
        return int(bonus)

    def calculate_product_free_bonus(self, bonus_pf: Dict[str, int]) -> int:
        def calculate_bonus_for_binary(binary_number: int) -> int:
            if binary_number >= 4 and binary_number < 8:
                return bonus_pf["pf4"]
            elif binary_number >= 8 and binary_number < 12:
                return bonus_pf["pf8"]
            elif binary_number >= 12 and binary_number < 16:
                return bonus_pf["pf12"]
            elif binary_number == 16:
                return bonus_pf["pf16"]
            else:
                return 0
        bonus = 0
        if self.position_number >= 1:
            bonus += calculate_bonus_for_binary(self.binary_number_1)
        if self.position_number >= 3:
            bonus += calculate_bonus_for_binary(self.binary_number_3)
        if self.position_number >= 5:
            bonus += calculate_bonus_for_binary(self.binary_number_5)
        if self.position_number >= 7:
            bonus += calculate_bonus_for_binary(self.binary_number_7)
        return bonus

    def calculate_matching_bonus(self, bonus_pf: Dict[str, int], total_paid_points: int) -> int:
        bonus = 0
        for child in self.children:
            if child.active:
                bonus += child.calculate_riseup_binary_bonus(bonus_pf) * 0.15
                for grandchild in child.children:
                    if grandchild.active:
                        bonus += grandchild.calculate_riseup_binary_bonus(bonus_pf) * 0.05
                        for great_grandchild in grandchild.children:
                            if great_grandchild.active:
                                bonus += great_grandchild.calculate_riseup_binary_bonus(bonus_pf) * 0.05
        return int(bonus)

    def calculate_car_bonus(self) -> int:
        if self.title_rank >= 4 and self.past_title_rank >= 4:
            return 100000
        return 0

    def calculate_house_bonus(self) -> int:
        if self.title_rank >= 5 and self.past_title_rank >= 5:
            return 150000
        return 0

    def calculate_sharing_bonus(self, total_paid_points: int) -> int:
        if self.title_rank == 3:
            return int(total_paid_points * 0.01)
        elif self.title_rank >= 4:
            return int(total_paid_points * 0.002)
        return 0

# ノード作成・ツリー構築用関数
def create_nodes_deterministic(layer_config: List[int], fixed_positions: List[int], active_prop) -> List[Node]:
    nodes = []
    node_counter = 1
    layer_nodes = {0: []}
    _active_prop = (100 - active_prop) / 100
    
    for i in range(layer_config[0]):
        pos = fixed_positions[0] if fixed_positions else 1
        node = Node(name=f"Node_{node_counter}", position_number=pos, active=True)
        nodes.append(node)
        layer_nodes[0].append(node)
        node_counter += 1

    for layer, num_children in enumerate(layer_config[1:], 1):
        layer_nodes[layer] = []
        for parent in layer_nodes[layer - 1]:
            for _ in range(num_children):
                pos = fixed_positions[layer] if layer < len(fixed_positions) else fixed_positions[-1]
                node = Node(
                    name=f"Node_{node_counter}",
                    position_number=pos,
                    parent_node=parent.name,
                    active=random.random() > _active_prop
                )
                nodes.append(node)
                layer_nodes[layer].append(node)
                parent.children.append(node)
                node_counter += 1
    return nodes

def build_node_hierarchy(nodes: List[Node]) -> List[Node]:
    node_dict = {node.name: node for node in nodes}
    root_nodes = []
    for node in nodes:
        if node.parent_node:
            if node.parent_node in node_dict:
                parent = node_dict[node.parent_node]
                if node not in parent.children:
                    parent.children.append(node)
        else:
            root_nodes.append(node)
    return root_nodes

def update_tree_numbers(node: Node,nodes) -> None:
    node.calculate_tree_number(nodes)
    for child in node.children:
        update_tree_numbers(child)


def calculate_all_bonuses(nodes: List[Node], bonus_rise_params: Dict[str, float], bonus_pf_params: Dict[str, int]) -> Dict[str, Tuple[int, int]]:
    total_paid_points = sum(node.paid_point for node in nodes)
    bonus_summary = {
        'riseup_bonus_30': [0, 0],
        'riseup_bonus_100': [0, 0],
        'riseup_bonus_1000': [0, 0],
        'riseup_bonus_10000': [0, 0],
        'product_free_bonus': [0, 0],
        'matching_bonus': [0, 0],
        'car_bonus': [0, 0],
        'house_bonus': [0, 0],
        'sharing_bonus': [0, 0]
    }

    for node in nodes:
        if not node.active:
            continue
        node.calculate_binary_numbers()

        riseup_binary_bonus = node.calculate_riseup_binary_bonus(bonus_rise_params)
        if riseup_binary_bonus > 0:
            binary_numbers = [node.binary_number_1, node.binary_number_3, node.binary_number_5, node.binary_number_7]
            for binary_number in binary_numbers:
                if binary_number >= 4:
                    if 4 <= binary_number <= 60:
                        bonus_summary['riseup_bonus_30'][0] += riseup_binary_bonus
                        bonus_summary['riseup_bonus_30'][1] += 1
                    elif 64 <= binary_number <= 200:
                        bonus_summary['riseup_bonus_100'][0] += riseup_binary_bonus
                        bonus_summary['riseup_bonus_100'][1] += 1
                    elif 204 <= binary_number <= 2000:
                        bonus_summary['riseup_bonus_1000'][0] += riseup_binary_bonus
                        bonus_summary['riseup_bonus_1000'][1] += 1
                    elif binary_number >= 2004:
                        bonus_summary['riseup_bonus_10000'][0] += riseup_binary_bonus
                        bonus_summary['riseup_bonus_10000'][1] += 1

        product_free_bonus = node.calculate_product_free_bonus(bonus_pf_params)
        if product_free_bonus > 0:
            bonus_summary['product_free_bonus'][0] += product_free_bonus
            bonus_summary['product_free_bonus'][1] += 1

        matching_bonus = node.calculate_matching_bonus(bonus_rise_params, total_paid_points)
        if matching_bonus > 0:
            bonus_summary['matching_bonus'][0] += matching_bonus
            active_count = (
                len([child for child in node.children if child.active]) +
                len([gc for child in node.children for gc in child.children if gc.active]) +
                len([ggc for child in node.children for gc in child.children for ggc in gc.children if ggc.active])
            )
            bonus_summary['matching_bonus'][1] += min(3, active_count)

        car_bonus = node.calculate_car_bonus()
        if car_bonus > 0:
            bonus_summary['car_bonus'][0] += car_bonus
            bonus_summary['car_bonus'][1] += 1

        house_bonus = node.calculate_house_bonus()
        if house_bonus > 0:
            bonus_summary['house_bonus'][0] += house_bonus
            bonus_summary['house_bonus'][1] += 1

        node.bonus_point = riseup_binary_bonus + product_free_bonus + matching_bonus + car_bonus + house_bonus
        node.total_bonus_point += node.bonus_point
    
    rank3 = 0
    rank4 = 0
    rank5 = 0
    rank6 = 0
    rank7 = 0
    rank8 = 0
    for node in nodes:
        if node.title_rank == 3:
            rank3 += 1
        elif node.title_rank == 4:
            rank4 += 1
        elif node.title_rank == 5:
            rank5 += 1
        elif node.title_rank == 6:
            rank6 += 1
        elif node.title_rank == 7:
            rank7 += 1
        elif node.title_rank == 8:
            rank8 += 1
        
    sharing_bonus = 0
    if rank3 >= 1:
        sharing_bonus += total_paid_points * 0.01
    if rank4 >= 1:
        sharing_bonus += total_paid_points * 0.002
    if rank5 >= 1:
        sharing_bonus += total_paid_points * 0.002
    if rank6 >= 1:
        sharing_bonus += total_paid_points * 0.002
    if rank7 >= 1:
        sharing_bonus += total_paid_points * 0.002
    if rank8 >= 1:
        sharing_bonus += total_paid_points * 0.002
    sharing_bonus = int(sharing_bonus)
    if sharing_bonus > 0:
        bonus_summary['sharing_bonus'][0] += sharing_bonus
        bonus_summary['sharing_bonus'][1] += 1
    node.bonus_point += sharing_bonus
    node.total_bonus_point += sharing_bonus

    return bonus_summary

# Streamlitアプリ本体
def main():
    st.title("ボーナス計算シミュレーション")
    st.markdown("外部からパラメータを渡して、シミュレーションを実行します。")

    st.sidebar.header("シミュレーションパラメータ")
    layer_config_str = st.sidebar.text_input("各層のノード数（カンマ区切り）", value="1,10,8,5,5,5,2")
    try:
        layer_config = [int(s.strip()) for s in layer_config_str.split(",")]
    except Exception as e:
        st.error("層数はカンマ区切りの整数で入力してください。")
        return

    fixed_positions_str = st.sidebar.text_input("各層のポジション番号（カンマ区切り）", value="7,5,3,3,3,1,1")
    try:
        fixed_positions = [int(s.strip()) for s in fixed_positions_str.split(",")]
    except Exception as e:
        st.error("ポジション番号はカンマ区切りの整数で入力してください。")
        return

    num_simulations = st.sidebar.number_input("シミュレーション回数", min_value=1, value=6, step=1)
    active_prop = st.sidebar.number_input("会員がアクティブになる確率（％）", min_value=10, max_value=100, value=70)

    st.sidebar.subheader("ライズアップボーナスの定数設定")
    bonus_rise_params = {
        "level1": st.sidebar.number_input("level1 (例: 3000)", value=3000.0),
        "level2": st.sidebar.number_input("level2 (例: 4000)", value=4000.0),
        "level3": st.sidebar.number_input("level3 (例: 5000)", value=5000.0),
        "level4": st.sidebar.number_input("level4 (例: 2000)", value=2000.0),
    }

    st.sidebar.subheader("プロダクトフリーボーナスの定数設定")
    bonus_pf_params = {
        "pf4": st.sidebar.number_input("pf4 (例: 10000)", value=10000, step=1000),
        "pf8": st.sidebar.number_input("pf8 (例: 7000)", value=7000, step=1000),
        "pf12": st.sidebar.number_input("pf12 (例: 4000)", value=4000, step=1000),
        "pf16": st.sidebar.number_input("pf16 (例: 1000)", value=1000, step=500),
    }

    if st.sidebar.button("計算開始"):
        st.write("シミュレーション実行中・・・")
        nodes = create_nodes_deterministic(layer_config, fixed_positions, active_prop)
        
        for node in nodes:
            node.tree_number = 0
        #    node.calculate_tree_number(nodes)
            if node.active:
                node.calculate_binary_numbers()
        root_nodes = build_node_hierarchy(nodes)
        for root in root_nodes:
            root.calculate_tree_number(nodes)
        st.write("ノード作成完了")

        simulation_results = []

        # シミュレーションループ
        for sim in range(num_simulations):
            total_bonus = 0
            st.write(f"#### シミュレーション {sim+1} 開始")
            for node in nodes:
                node.paid_point=0
                node.set_position(node.position_number)
                node.update_title_rank()
            bonus_summary = calculate_all_bonuses(nodes, bonus_rise_params, bonus_pf_params)
            total_bonus = sum(node.bonus_point for node in nodes)
            simulation_results.append((sim + 1, bonus_summary, total_bonus))

            # シミュレーションごとの結果を表示
            st.write(f"**シミュレーション{sim+1}のボーナス内訳 [合計金額, 件数]:**")
            st.json(bonus_summary)
            st.write(f"**シミュレーション{sim+1}の総ボーナス金額: {total_bonus}**")

            # 次のシミュレーションのためにノードを更新
            for node in nodes:
                node.activate(active_prop)
                node.set_position(node.position_number)
                for child in node.children:
                    child.activate(active_prop)
            #root_nodes = build_node_hierarchy(nodes)
            #for root in root_nodes:
            #    update_tree_numbers(root)
            tree_number_lis = []
            for node in nodes:
                node.tree_number = 0
                #update_tree_numbers(node,_nodes)
                #node.calculate_tree_number(nodes)
                #tree_number_lis.append(node.tree_number)
                if node.active:
                    node.binary_number_1 = 0
                    node.binary_number_3 = 0
                    node.binary_number_5 = 0
                    node.binary_number_7 = 0
                    node.calculate_binary_numbers()
            root_nodes = build_node_hierarchy(nodes)
            for root in root_nodes:
                root.active = True
                root.calculate_tree_number(nodes)
            #st.write(tree_number_lis)
            st.write(f"シミュレーション {sim+1} 完了")
            time.sleep(1)

if __name__ == "__main__":
    main()
